# production terraform

## Getting Started

```bash
cd terraform/prod
terraform plan
terraform apply
```

## Push docker image to ecr

```bash
docker build --platform=linux/amd64 -t password-database ./docker/mysql
docker tag password-manager-db:local 043309350986.dkr.ecr.ap-northeast-1.amazonaws.com/password-manager-db:latest
docker push 043309350986.dkr.ecr.ap-northeast-1.amazonaws.com/password-manager-db:latest
```
