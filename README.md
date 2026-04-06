### Criar um projeto no PyCharm com o python  na versão 12.7

### Abrir o terminal e instalar 
•	pip install "fastapi[standard]"

### Gere o arquivo para deploy futuro requirements.txt
### Caso com pip:

	pip freeze > requirements.txt

### Caso uso do poetry	

	poetry export -f requirements.txt --output requirements.txt --without-hashes

### Gere o arquivo para desinstalar todas as bibliotecas
	
    pip freeze > uninstall.txt

### Para retirar execute:

	pip uninstall -r uninstall.txt -y

### Para executar o projeto execute:

	fastapi dev main.py


### Estrutura do projeto

	domain/__init__.py 

	schemas/__init__.py 

	repositories/__init__.py 

	services/__init__.py 

	api/__init__.py 

	api/routes/__init__.py


### Configurando o venv

sudo apt install python3.12-venv

source venv/bin/activate

source venv/bin/deactivate