
# Docker Runner / Cloudwatch Logger

This repository runs a docker image and sends all the logs to Cloudwatch using boto3



## Authors

- [@bshadmehr98](https://github.com/bshadmehr98)


## Run Locally

Clone the project

```bash
  git clone https://github.com/bshadmehr98/docker-log-cloudwatch.git
```

Go to the project directory

```bash
  cd docker-log-cloudwatch
```

Install dependencies

```bash
  pip install -r requirements.txt
```

Use help for a complete descriptions

```bash
  python main.py --help
```

Run the code:

```bash
  python main.py --docker-image python --bash-command <Bash-Command> --aws-cloudwatch-group <Cloudwatch-Group-Name> --aws-cloudwatch-stream <Cloudwatch-Stream-Name> --aws-access-key-id <AWS-access-key-id> --aws-secret-access-key <AWS-Secret-access-key> --aws-region <AWS-region>
```


