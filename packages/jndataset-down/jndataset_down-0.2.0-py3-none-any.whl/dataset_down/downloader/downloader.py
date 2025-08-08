import os
import json
import hashlib
import time
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List
from tqdm import tqdm
import requests
import signal
import threading
from dataset_down.client.AuthClient import auth_client
from dataset_down.config.constants import SERVER_URL,OPERATE_URL,DOWNLOAD_URL
from dataset_down.update.update_check import update_check
from dataset_down.utils.retryable import retry_with_backoff
from dataset_down.utils.system_utils import caculate_download_worker_num



lock = threading.Lock()

interrupt_event = threading.Event()

base_headers = {
    "accept": "application/json",
}
headers_post_base = {
    **base_headers,
    "Content-Type": "application/json",
}

def http_authorization_header() -> dict:
        try:
            header_dict = headers_post_base
            token = auth_client.get_token()
            header_dict['Authorization'] = token
        except Exception as e:
            print(f"{e}")
            sys.exit(-1)
        return header_dict


def signal_handler(sig, frame):
        print("\ns检测到 Ctrl+C,正在强制退出...\n")
        interrupt_event.set()
        os._exit(1)

class Downloader:
    def __init__(self, dataset_id : str , source_path: str, version: str = 'master' , download_dir: str ='.', max_workers=4):
        self.task_id = "default-task_id" 
        self.dataset_id = dataset_id
        self.version = version
        self.source_path = source_path
        self.download_dir = download_dir
        self.max_workers = max_workers  # 并发线程数
        self.chunk_dirs = []
        self.total_bytes = 0
        self.downloaded_bytes = 0
        self.start_time = None
        
        os.makedirs(self.download_dir, exist_ok=True)
        
        
    def create_task(self):
        create_task_url = f"{SERVER_URL}{OPERATE_URL}/createTask"
        data = {
            "datasetId": self.dataset_id,
            "version": self.version,
        }
        response = requests.post(create_task_url, data=json.dumps(data), headers=http_authorization_header(), timeout=3)
        response.raise_for_status()
        if response.status_code == 200:
            ret_code = response.json()["code"]
            if ret_code == 0:
                self.task_id = response.json()["data"]["taskId"]
                if self.task_id != None and self.task_id != "":
                    print("create task success,taskId: %s" % self.task_id)
                    return
        raise Exception("create task failed")
        
    
    @retry_with_backoff(max_retries=3, base_delay=1, max_delay=5)
    def list_files(self):
        print("获取下载文件信息中...\n")
        """列出所有文件"""
        list_url = f"{SERVER_URL}{OPERATE_URL}pre_download_list"
        query_dict = { "datasetId": self.dataset_id, "version": self.version , "filePath": self.source_path}
        response = requests.post(list_url, data=json.dumps(query_dict),headers=http_authorization_header(),timeout=300)
        response.raise_for_status()
        if response.status_code == 200:
            ret_code = response.json()['code']
            if ret_code == 0:
                objects = response.json()['data']['objects']
                files = []
                for obj in objects:
                    files.append(obj['relPath'])
                return files
            else:
                raise Exception(response.json()['message'])
        else:
            print(f"list error: {response.status_code},query_dict: {query_dict}")
            raise Exception(f"list error: {response.status_code},query_dict: {query_dict}")
        
    
    @retry_with_backoff(max_retries=3, base_delay=1, max_delay=5)    
    def pre_downLoad(self, file_path):
        pre_download_url = f"{SERVER_URL}{DOWNLOAD_URL}preDownLoad"
        query_dict = {
            "taskId": self.task_id,
            "datasetId": self.dataset_id,
            "version": self.version,
            "filePath": file_path,
        }
        response = requests.post(pre_download_url, data=json.dumps(query_dict),headers=http_authorization_header(),timeout=30)
        response.raise_for_status()
        if response.status_code == 200:
            ret_code = response.json()["code"]
            if ret_code == 0:
                data = response.json()["data"]
                return {
                    "key": data["key"],
                    "relPath": data["relPath"],
                    "fileSize": data["fileSize"],
                    "fileParts": data["fileParts"],
                    "sha256": data["sha256"],
                }
            else:
                raise Exception(f"failed to preDownLoad {file_path},ret_code:{ret_code}")
        else:
            raise Exception("failed to preDownLoad {file_path},response.status_code:{response.status_code}")
        
        
    def report(self,operate_type,exec_state,progress,file_size,begin_time,remaining_time,end_time = None):
        if True:
            return
        report_url = f"{SERVER_URL}{OPERATE_URL}report"
        report_data = {
            "taskId":self.task_id,
            "datasetId":self.dataset_id,
            "version":self.version,
            "filePath": self.source_path,
            "operateType": operate_type,
            "execState": exec_state,
            "progress": progress,
            "fileSize": file_size,
            "beginTime": begin_time,
            "endTime" : end_time,
            "remainingTime": remaining_time
        }
        response = requests.post(report_url, data=json.dumps(report_data),headers=http_authorization_header(),timeout=3)
        response.raise_for_status()
        if response.status_code == 200:
            ret_code = response.json()["code"]
            if ret_code == 0:
                data = response.json()["data"]
                return data
            else:
                raise Exception(f"failed to report upload progress, ret_code: {ret_code}")
        else:
            raise Exception(f"failed to report upload progress. status_code: {response.status}, reason: {response.reason}")
    
    
    def pre_download(self,file_paths: List):
        with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
            # 提交所有预下载任务
            future_to_path = {
                executor.submit(self.pre_downLoad, file_path): file_path 
                for file_path in file_paths
            }
    
            # 收集结果
            files_info = []
            with tqdm(total=len(file_paths), desc="Preparing",unit="file") as progress_bar: 
                for future in as_completed(future_to_path):
                    file_path = future_to_path[future]
                    try:
                        file_info = future.result()
                        files_info.append(file_info)
                        progress_bar.update(1)
                        progress_bar.set_postfix( {"完成": file_path})
                    except Exception as e:
                        progress_bar.set_postfix( {"失败": file_path})
                        print(f"pre download {file_path} failed: {e}")
                        raise
                return files_info
    
    
        
        
    def download(self):
        file_paths = self.list_files()
        files_info = []
        files_info = self.pre_download(file_paths)
        self.download_folder(files_info)
        self.delete_chunks_dirs()
        print("download completed")
            
            
    def download_folder(self, files_info):
        self.total_bytes = sum(file_info['fileSize'] for file_info in files_info)
        self.downloaded_bytes = 0
        self.start_time = time.time()
        
        
        """下载整个文件夹"""
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for file_info in files_info:
                future = executor.submit(
                    self.download_file,
                    file_info['key'],
                    file_info['relPath'],
                    file_info['fileSize'],
                    file_info['fileParts'],
                    file_info['sha256']
                )
                futures.append(future)
                
            
            
            completed_set = set()
            total = len(futures)
            desc = "整体进度"
            with tqdm(total=total, desc=desc) as progress_bar:
                while len(completed_set) < total:
                    if self.is_interrupted():
                        print("\n检测到中断信号,正在取消未完成的任务...")
                        for future in futures:
                            future.cancel()
                        executor.shutdown(wait=False)
                        raise Exception("任务被中断")

                    newly_completed = []
                    for future in futures:
                        if future in completed_set:
                            continue
                        if future.done():
                            try:
                                future.result()  # 触发异常抛出
                            except Exception as e:
                                print(f"下载出错: {e}")
                                raise e
                            newly_completed.append(future)

                    for f in newly_completed:
                        completed_set.add(f)
                        progress_bar.update(1)
                    
                    try:
                        current_progress_float = 0.0
                        remaining_time = 0 
                        with lock:
                            if self.downloaded_bytes > 0:
                                elapsed = time.time() - self.start_time
                                speed = self.downloaded_bytes / elapsed
                                remaining_bytes = self.total_bytes - self.downloaded_bytes
                                eta_seconds = remaining_bytes / speed
                                remaining_time = eta_seconds
                                eta_str = time.strftime("%H:%M:%S", time.gmtime(eta_seconds))
                                progress_bar.set_postfix({"speed":f"{speed/1024/1024:.2f} MB/s", "eta": eta_str})
                                current_progress_float = self.downloaded_bytes / self.total_bytes
                        self.report('DOWNLOAD','DOWNLOADING',current_progress_float,file_size=self.total_bytes,begin_time=self.start_time,remaining_time=remaining_time,end_time=None)
                    except Exception as e:
                        print(f"failed to report progress,msg: {e}")
                       
                    time.sleep(2)  # 避免 CPU 占用过高
                try:
                    self.report('DOWNLOAD','DOWNLOAD_COMPLETE',1.0,file_size=self.total_bytes,begin_time=self.start_time,remaining_time=0,end_time=time.time())
                except Exception as e:
                    print(f"failed to report progress,msg: {e}")
            

    def download_file(self, key, relative_path,file_size, file_parts, sha256):
        """下载单个文件"""
        # 构建本地路径
        relative_path = os.path.normpath(relative_path)
        local_dir = os.path.join(self.download_dir, os.path.dirname(relative_path))
        local_file_path = os.path.join(self.download_dir, relative_path)
        chunk_dir = os.path.join(local_dir, '.chunks')
        with lock:
            self.chunk_dirs.append(chunk_dir)
        
        cache_dir = os.path.join(chunk_dir,  os.path.basename(relative_path) + '.cache')
        
        with lock:
            # 并发创建目录会有问题
            os.makedirs(local_dir, exist_ok=True)
            os.makedirs(chunk_dir, exist_ok=True)
            os.makedirs(cache_dir, exist_ok=True)

        # 如果文件已存在且校验通过
        if os.path.exists(local_file_path) and self.verify_sha256(local_file_path, sha256):
            with lock:
                os.rmdir(cache_dir)
                return

        # 获取文件大小
        if not file_size or file_size <= 0:
            print(f"File size for {relative_path} is invalid or zero. Skipping download.")
            return

        if not file_parts or len(file_parts) == 0:
            print(f"File parts for {relative_path} is invalid or empty. Skipping download.")
            return
        # 计算分片数量
        num_chunks = len(file_parts)
        
        # 检查已下载的分片
        chunks_to_download = self.check_existing_chunks(cache_dir, file_parts , num_chunks)
        
        downloaded_before = self.calculate_downloaded_bytes(cache_dir, file_parts, num_chunks)
        with lock:
            self.total_bytes = self.total_bytes - downloaded_before
        
        
        # 下载进度条
        progress_bar = tqdm(
            total=file_size,
            desc=f"下载 {relative_path}",
            unit="B",
            unit_scale=True,
            initial=downloaded_before,
        )

        # 并发下载分片
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            futures = []
            for i in chunks_to_download:
                future = executor.submit(
                    self.download_chunk,
                    file_parts, 
                    cache_dir, 
                    i, 
                    progress_bar
                )
                futures.append(future)

            for future in as_completed(futures):
                if interrupt_event.is_set():
                    for future in futures:
                        future.cancel()
                    executor.shutdown(wait=False)
                    raise KeyboardInterrupt()
                try:
                    future.result()
                except Exception as e:
                    print(f"分片下载失败: {e}")
                    progress_bar.close()
                    return

        progress_bar.close()

        # 合并分片
        if self.merge_chunks(cache_dir, num_chunks, local_file_path):
            # 校验SHA256
            if self.verify_sha256(local_file_path,sha256):
                with lock:
                # 清理分片文件
                    self.cleanup_chunks(cache_dir)
                    os.rmdir(cache_dir)
    
    def check_existing_chunks(self, cache_dir, file_parts, num_chunks):
        """检查已存在的分片"""
        existing_chunks = []
        for i in range(num_chunks):
            cur_part = file_parts[i]
            range_start = cur_part['rangeStart']
            range_end = cur_part['rangeEnd']
            expected_size = range_end - range_start + 1
            
            chunk_path = os.path.join(cache_dir, f"part_{i:03d}.tmp")
            
            if os.path.exists(chunk_path) and os.path.getsize(chunk_path) == expected_size:
                existing_chunks.append(i)
        
        return [i for i in range(num_chunks) if i not in existing_chunks]

    def calculate_downloaded_bytes(self, cache_dir, file_parts,num_chunks):
        """计算已下载字节数"""
        total = 0
        for i in range(num_chunks):
            chunk_path = os.path.join(cache_dir, f"part_{i:03d}.tmp")
            if os.path.exists(chunk_path):
                cur_part = file_parts[i]
                range_start = cur_part['rangeStart']
                range_end = cur_part['rangeEnd']
                expected_size = range_end - range_start + 1
                if expected_size == os.path.getsize(chunk_path):
                    total += os.path.getsize(chunk_path)
        return total

    @retry_with_backoff(max_retries=3, base_delay=1, max_delay=5)
    def download_chunk(self, file_parts, cache_dir, chunk_index, progress_bar):
        """下载单个分片"""
        url = file_parts[chunk_index]['signUrl']
        start = file_parts[chunk_index]['rangeStart']
        end = file_parts[chunk_index]['rangeEnd']
        
        headers = {'Range': f'bytes={start}-{end}'}
        chunk_path = os.path.join(cache_dir, f"part_{chunk_index:03d}.tmp")
        
        try:
            with requests.get(url, headers=headers, stream=True, timeout=300) as r:
                r.raise_for_status()
                
                with open(chunk_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=1024*1024):
                        if self.is_interrupted():
                            print(f"\n cache_dir: {cache_dir} 分片 {chunk_index} 下载已中断")
                            progress_bar.close()
                            time.sleep(1)
                            return 
                        if chunk:
                            f.write(chunk)
                            progress_bar.update(len(chunk))
                            with lock:
                                self.downloaded_bytes += len(chunk)
                            
        except Exception as e:
            print(f"下载分片 {chunk_index} 失败: {e}")
            if os.path.exists(chunk_path):
                os.remove(chunk_path)
            raise e

    def merge_chunks(self, cache_dir, num_chunks, output_path):
        """合并分片"""
        try:
            with open(output_path, 'wb') as output_file:
                for i in range(num_chunks):
                    chunk_path = os.path.join(cache_dir, f"part_{i:03d}.tmp")
                    with open(chunk_path, 'rb') as chunk_file:
                        output_file.write(chunk_file.read())
                    os.remove(chunk_path)
            return True
        except Exception as e:
            print(f"合并分片失败: {e}")
            raise e
            #return False

    def verify_sha256(self, file_path, expected_sha256):
        """验证SHA256"""
        sha256_hash = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(chunk)
            return sha256_hash.hexdigest() == expected_sha256
        except Exception as e:
            print(f"校验失败: {e}")
            raise e
            #return False

    def cleanup_chunks(self, cache_dir):
        """清理分片文件"""
        for file in os.listdir(cache_dir):
            os.remove(os.path.join(cache_dir, file))
    @retry_with_backoff(max_retries=3, base_delay=1, max_delay=5)
    def delete_chunks_dirs(self):
        for dir in self.chunk_dirs:
            if os.path.exists(dir) and os.path.isdir(dir) and len(os.listdir(dir)) == 0:
                os.rmdir(dir)
            

    def is_interrupted(self):
        """检查是否被中断"""
        return interrupt_event.is_set()
            






def login(ak: str, sk: str): 
    try:
        auth_client.login(ak, sk)
        update_check()
    except Exception as e:
        raise e 
    


    
            
def download(dataset_id: str, source_path: str, target_path: str,version = 'master'):
    if not dataset_id or len(dataset_id) == 0:
        raise ValueError("dataset_id cannot be empty")
    
    if not source_path or len(source_path) == 0:
        raise ValueError("source_path cannot be empty")
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    
    if not target_path:
        target_path = os.getcwd()
    if target_path.startswith('~'):
        target_path = os.path.expanduser(target_path)
    target_path = os.path.realpath(target_path)
    
    downloader = Downloader(
            dataset_id=dataset_id,
            source_path=source_path,
            version=version,
            download_dir=target_path,
            max_workers=caculate_download_worker_num()
            )
    
    downloader.download()
