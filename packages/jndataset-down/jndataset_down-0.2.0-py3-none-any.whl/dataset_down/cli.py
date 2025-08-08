import click
from dataset_down.downloader.downloader import download as download_inner
from dataset_down.downloader.downloader import login as login_inner
from dataset_down.update.update_check import update_check
from dataset_down.utils.system_utils import stop_dataset_down_process
from dataset_down.client.AuthClient import auth_client
def validate_input(ctx, param, value):
    if not value or value.strip() == "":
        raise click.BadParameter("输入不能为空或空格")
    return value

@click.group()
def cli():
    pass

@cli.command()
@click.option("--dataset-id", required=True, help="数据集 ID",callback=validate_input)
@click.option("--version", default="master", help="版本号,默认是master",callback=validate_input)
@click.option("--source-path", required=True, help="源文件路径,如果是目录，那么就下载整个目录",callback=validate_input)
@click.option("--target-path", default=".", help="目标保存路径 (默认: 当前目录)",callback=validate_input)
def download(dataset_id: str, version: str, source_path: str , target_path: str):
    """下载文件或者整个文件夹"""
    try:
        update_check()
        download_inner(
            dataset_id=dataset_id,
            source_path=source_path,
            target_path=target_path,
            version=version
        )
    except Exception as e:
        print(f"下载失败: {e}")
        

@cli.command()
@click.option("--ak", required=True, help="Access Key")
@click.option("--sk", required=True, help="Secret Key")
def login(ak: str, sk: str):
    """登录"""
    try:
        login_inner(ak, sk)
        click.echo("登录成功")
    except Exception as e:
        click.echo(f"登录失败,请检查AK/SK是否输入正确! msg: {e}")


@cli.command()
def stop_running_downloading_process():
    """停止正在运行的下载进程"""
    stop_dataset_down_process()

def main():
    cli()

if __name__ == "__main__":
    main()