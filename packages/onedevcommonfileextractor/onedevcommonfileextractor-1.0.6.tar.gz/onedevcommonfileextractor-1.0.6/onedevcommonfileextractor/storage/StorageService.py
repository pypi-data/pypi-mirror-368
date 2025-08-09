import io
import oci

from .JobSphereOCIObjectStorage import JobSphereOCIObjectStorage

class OCIStorageManager:
    def __init__(self):
        """
        Inicializa a classe com o contexto IazzieContext.
        """
        # Instancia JobSphereOCIObjectStorage para verificar o ambiente
        # A instância precisa de um bucket, 'tasks' é um padrão seguro.
        self.oci_storage_helper = JobSphereOCIObjectStorage('tasks') 
        self.environment = self.oci_storage_helper.environment


    def download_file(self, file_name, task_id=0, chat_id=0):
        """
        Realiza o download, verificando IDs e baixando o arquivo do Object Storage.

        Args:
            file_name: Nome do arquivo a ser processado.

        Returns:
            Bytes do arquivo baixado ou mensagem de erro em caso de falha.
        """
        try:
            if task_id <= 0 and chat_id <= 0:
                return "Nenhum arquivo para baixar: task_id e chat_id estão vazios ou inválidos."

            if task_id > 0:
                base_path = f"{task_id}/{file_name}"
                container_name = 'tasks'
            elif chat_id > 0:
                base_path = f"{chat_id}/{file_name}"
                container_name = 'chats'

            # Adiciona o prefixo 'dev/' se o ambiente for de desenvolvimento
            blob_name = self.oci_storage_helper.get_object_name(base_path)
            
            print(f"Tentando baixar o blob: {blob_name} do container: {container_name}")

            # Baixar arquivo como bytes
            blob_data = download_file_as_bytes(container_name, blob_name)
            if blob_data is None:
                raise ValueError("Falha no download: o arquivo não foi encontrado ou retornou vazio.")

            print(f"Arquivo {file_name} baixado com sucesso.")

            file = io.BytesIO(blob_data)

            return file

        except Exception as exception:
            print(f"Erro no processamento do arquivo: {exception}")
            return str(exception)
        
        
    def list_storage_files_with_context(self, task_id=0, chat_id=0):
        """
        Lista os arquivos (objetos) disponíveis em um bucket específico, considerando task_id ou chat_id do servicer.


        Returns:
            list: Uma lista com os nomes dos arquivos encontrados no bucket, filtrados pelo contexto.
        """
        try:
            # Determinar o prefixo baseado no contexto
            base_prefix = ""
            if task_id > 0:
                base_prefix = f"{task_id}/"
                bucket_name = "tasks"
            elif chat_id > 0:
                base_prefix = f"{chat_id}/"
                bucket_name = "chats"
            else:
                print("Nenhum contexto válido: task_id e chat_id estão vazios ou inválidos.")
                return []

            # Adiciona o prefixo 'dev/' se o ambiente for de desenvolvimento
            prefix = self.oci_storage_helper.get_object_name(base_prefix)
            print(f"Listando arquivos com prefixo: {prefix}")

            # Configuração do OCI Storage
            oci_storage = JobSphereOCIObjectStorage(bucket_name)
            object_storage_client = oci_storage.get_object_storage_client()
            namespace = oci_storage.get_namespace()

            # Listar objetos no bucket com o prefixo
            list_objects_response = object_storage_client.list_objects(
                namespace,
                bucket_name,
                prefix=prefix
            )

            # Retorna os nomes dos objetos encontrados
            file_names = [obj.name for obj in list_objects_response.data.objects]
            print(f"Arquivos no bucket '{bucket_name}' com prefixo '{prefix}': {file_names}")

            return file_names
        except oci.exceptions.ServiceError as e:
            print(f"Erro ao listar arquivos do bucket {bucket_name}: {str(e)}")
            return []
        except Exception as e:
            print(f"Erro inesperado ao listar arquivos do bucket {bucket_name}: {str(e)}")
            return []
        
        
    def upload_file(self, file_name, file_data, task_id=0, chat_id=0):
        if (not task_id and not chat_id) and (task_id <= 0 and chat_id <= 0):
            return "Nenhum arquivo para baixar: task_id e chat_id estão vazios ou inválidos."

        if task_id and task_id > 0:
            print(f"task_id está definido: {task_id}")
            blob_name = f"{task_id}/{file_name}"
            container_name = 'tasks'
        elif chat_id and chat_id > 0:
            print(f"chat_id está definido: {chat_id}")
            blob_name = f"{chat_id}/{file_name}"
            container_name = 'chats'
        else:
            print("Não possui task_id e nem chat_id.")

        oci_storage = JobSphereOCIObjectStorage(container_name)
        object_storage_client = oci_storage.get_object_storage_client()
        namespace = oci_storage.get_namespace()
        bucket_name = oci_storage.get_bucket_name()

        object_name = blob_name
        object_storage_client.put_object(
            namespace,
            bucket_name,
            object_name,
            file_data
        )

        print(f"Arquivo {blob_name} enviado para o OCI Object Storage.")

        return object_name


async def upload_files(task_id, file_data_list):
    oci_storage = JobSphereOCIObjectStorage('tasks')
    object_storage_client = oci_storage.get_object_storage_client()
    namespace = oci_storage.get_namespace()
    bucket_name = oci_storage.get_bucket_name()

    for filename, file_data in file_data_list:
        object_name = f"{task_id}/{filename}"
        object_storage_client.put_object(
            namespace,
            bucket_name,
            object_name,
            file_data
        )
        print(f"Arquivo {filename} enviado para o OCI Object Storage.")

async def copy_bucket_list_files(task_id, bucket_list):
    destination_folder = f"{task_id}"

    oci_storage_source = JobSphereOCIObjectStorage('workloads')
    oci_storage_destination = JobSphereOCIObjectStorage('tasks')

    object_storage_client = oci_storage_source.get_object_storage_client()
    namespace = oci_storage_source.get_namespace()
    destination_region = oci_storage_destination.config['region']

    for bucket in bucket_list:
        list_objects_response = object_storage_client.list_objects(namespace, bucket)
        for obj in list_objects_response.data.objects:
            source_object_name = obj.name
            destination_object_name = source_object_name.replace(bucket, destination_folder)

            copy_object_details = oci.object_storage.models.CopyObjectDetails(
                source_object_name=source_object_name,
                destination_bucket=oci_storage_destination.get_bucket_name(),
                destination_namespace=namespace,
                destination_object_name=destination_object_name,
                destination_region=destination_region  # Define a região de destino
            )

            object_storage_client.copy_object(
                namespace,
                bucket,
                copy_object_details
            )
            print(f"Arquivo {source_object_name} copiado para {destination_object_name} no bucket de destino.")

async def copy_object_key_list_files(task_id, object_key_list):
    destination_folder = f"{task_id}"

    oci_storage_destination = JobSphereOCIObjectStorage('tasks')
    object_storage_client = oci_storage_destination.get_object_storage_client()
    namespace = oci_storage_destination.get_namespace()
    destination_bucket_name = oci_storage_destination.get_bucket_name()
    destination_region = oci_storage_destination.config['region']

    for object_key_url in object_key_list:
        # Extrair o nome do objeto da URL
        object_name = object_key_url.split('/')[-1]
        destination_object_name = f"{destination_folder}/{object_name}"

        # Obter detalhes do objeto de origem
        source_bucket_name = "workloads"
        source_object_name = object_key_url

        copy_object_details = oci.object_storage.models.CopyObjectDetails(
            source_object_name=source_object_name,
            destination_bucket=destination_bucket_name,
            destination_namespace=namespace,
            destination_object_name=destination_object_name,
            destination_region=destination_region  # Define a região de destino
        )

        object_storage_client.copy_object(
            namespace,
            source_bucket_name,
            copy_object_details
        )
        print(f"Arquivo {object_name} copiado para {destination_object_name} no bucket de destino.")

def download_file_as_bytes(bucket_name, object_name):
    oci_storage = JobSphereOCIObjectStorage(bucket_name)
    object_storage_client = oci_storage.get_object_storage_client()
    namespace = oci_storage.get_namespace()

    # Faz o download do objeto do bucket
    try:
        get_object_response = object_storage_client.get_object(
            namespace,
            bucket_name,
            object_name
        )

        # Retorna os bytes do conteúdo do objeto
        return get_object_response.data.content
    except oci.exceptions.ServiceError as e:
        print(f"Erro ao baixar o arquivo {object_name}: {str(e)}")
        return None
    
    
def download_file_as_stream(bucket_name, object_name):
    blob_data = download_file_as_bytes(bucket_name, object_name)

    return io.BytesIO(blob_data)

def upload_stream(task_id, file_name, stream):
    oci_storage = JobSphereOCIObjectStorage('tasks')
    object_storage_client = oci_storage.get_object_storage_client()
    namespace = oci_storage.get_namespace()
    bucket_name = oci_storage.get_bucket_name()

    object_name = f"{task_id}/{file_name}"
    result = object_storage_client.put_object(
        namespace,
        bucket_name,
        object_name,
        stream
    )
    print(f"Arquivo {file_name} enviado para o OCI Object Storage.")      
    return result
