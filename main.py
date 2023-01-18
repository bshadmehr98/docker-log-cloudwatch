from runner import Runner


import click


@click.command()
@click.option("--docker-image", help="Docker image you want to run", required=True)
@click.option("--bash-command", help="Bash command for the container", required=True)
@click.option(
    "--aws-cloudwatch-group",
    help="Name of the cloudwatch group you want to use for this container",
    required=True,
)
@click.option(
    "--aws-cloudwatch-stream",
    help="Name of the cloudwatch stream you want to use for this containrs log",
    required=True,
)
@click.option("--aws-access-key-id", help="AWS access key", required=True)
@click.option("--aws-secret-access-key", help="AWS secret access key", required=True)
@click.option("--aws-region", help="AWS region", required=True)
def main(
    docker_image,
    bash_command,
    aws_cloudwatch_group,
    aws_cloudwatch_stream,
    aws_access_key_id,
    aws_secret_access_key,
    aws_region,
):
    """A program that runs the container and sends the logs to cloudwatch"""
    r = Runner(
        docker_image,
        ["/bin/bash", "-c", bash_command],
        aws_cloudwatch_group,
        aws_cloudwatch_stream,
        aws_access_key_id,
        aws_secret_access_key,
        aws_region,
        debug=False,
    )
    r.runner()


if __name__ == "__main__":
    main()
