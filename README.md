# Employee Task Manager (Frontend + Flask + MariaDB)

## Step 1: Run locally with Docker Compose
    docker compose up --build
    # open http://localhost:8080
    curl http://localhost:8080/api/employees

Reset the database: `docker compose down -v`

## Step 2: Deploy to Kubernetes (minikube / kind / kubeadm)

Build images:

    docker build -t employee-backend:1.0 ./backend
    docker build -t employee-frontend:1.0 ./frontend

Load into the cluster (no registry needed):

    minikube image load employee-backend:1.0
    minikube image load employee-frontend:1.0
    # kind: kind load docker-image employee-backend:1.0 employee-frontend:1.0

Deploy (order matters):

    kubectl apply -f k8s/namespace.yaml
    kubectl create configmap mariadb-init --from-file=database/init.sql -n employee-app
    kubectl apply -f k8s/mariadb-secret.yaml -f k8s/mariadb-configmap.yaml -f k8s/mariadb-pvc.yaml
    kubectl apply -f k8s/mariadb-deployment.yaml -f k8s/mariadb-service.yaml
    kubectl apply -f k8s/backend-deployment.yaml -f k8s/backend-service.yaml
    kubectl apply -f k8s/frontend-deployment.yaml -f k8s/frontend-service.yaml

Verify and open:

    kubectl get all,pvc -n employee-app
    minikube service frontend -n employee-app      # or http://<node-ip>:30080

## Practice commands
    kubectl logs deploy/backend -n employee-app
    kubectl exec -it deploy/mariadb -n employee-app -- mariadb -uappuser -p employee_db
    kubectl delete pod -l app=mariadb -n employee-app    # data survives (PVC)

## Next levels
- Backup: kubectl exec deploy/mariadb -n employee-app -- mariadb-dump -uroot -p<pw> employee_db > backup.sql, then a CronJob
- Ingress, then a Jenkinsfile (build, Trivy scan, push to Docker Hub, deploy)

Note: init.sql only runs on first start with an empty data volume.
