import oci
import os

class JobSphereOCIObjectStorage:
    def __init__(self, bucket_name):
        self.bucket_name = bucket_name

        # Caminho absoluto para o diretório de configuração
        config_directory = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'oci')

        # Caminho absoluto para o arquivo de configuração
        config_file = os.path.join(config_directory, 'config')

        # Carregar a configuração a partir do arquivo
        self.config = oci.config.from_file(file_location=config_file, profile_name='DEFAULT')

        # Atualizar o caminho da chave privada para ser absoluto
        self.config['key_file'] = os.path.join(config_directory, 'oci_api_key.pem')

        # Inicializar o cliente de Object Storage
        self.object_storage_client = oci.object_storage.ObjectStorageClient(self.config)
        self.namespace = self.object_storage_client.get_namespace().data

    def get_object_storage_client(self):
        return self.object_storage_client

    def get_namespace(self):
        return self.namespace

    def get_bucket_name(self):
        return self.bucket_name

    @property
    def environment(self):
        """Retorna o ambiente atual baseado na configuração."""
        # Verifica se existe uma variável de ambiente específica
        # Padrão é 'prod' (produção) - só adiciona prefixo se for 'dev'
        env = os.getenv('ENVIRONMENT', 'prod')
        return env.lower()

    def get_object_name(self, base_path):
        """
        Retorna o nome do objeto com prefixo de ambiente se necessário.
        
        Args:
            base_path: Caminho base do objeto (ex: '12345/arquivo.pdf')
            
        Returns:
            Nome do objeto com prefixo de ambiente se for dev (ex: 'dev/12345/arquivo.pdf')
        """
        if self.environment == 'dev':
            return f"dev/{base_path}"
        return base_path
