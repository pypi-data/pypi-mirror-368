from time import sleep
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from zenpy import Zenpy
from zenpy.lib.api_objects import CustomField, Ticket, Comment, User
from zenpy.lib.exception import RecordNotFoundException, APIException
from dataclasses import dataclass
from typing import Optional, Dict, Any, Iterable, List
import traceback

import requests
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
session = requests.Session()
session.verify = True



options = ChromeOptions()

TIMEOUT = 300

class Driver_Selenium():

    def criar_driver(local=False, timeout='24h'):
        if local:
            options = ChromeOptions()
            driver = webdriver.Chrome(options=options)
        else:
            options = ChromeOptions()
            options.browser_version = "latest"
            options.set_capability("browserName", "chrome")
            options.set_capability(
                "selenoid:options", {
                    "enableVNC": True,
                    "sessionTimeout": timeout
                }
            )
            driver = webdriver.Remote(
                command_executor="http://201.23.65.205:4444/wd/hub",
                options=options
            )
        driver.maximize_window()
        return driver

    def verificar_e_recriar_driver(driver):
        """Verifica se o driver está ativo. Se não, cria um novo e o retorna."""
        if driver:
            try:
                _ = driver.title
                print("Sessão do driver está ativa.")
                return driver 
            except Exception:
                print("Sessão do driver inativa. Recriando...")
                try:
                    driver.quit()
                except Exception:
                    pass

        novo_driver = Driver_Selenium.criar_driver()
        return novo_driver


class Zendesk_Selenium:

    def __init__(self, driver, usuario, senha, instancia):
        self.driver = driver
        self.usuario = usuario
        self.senha = senha
        self.instancia = instancia


    def login(self):
        link = self.instancia
        link = f'https://{link}.zendesk.com/access/normal'
        self.driver.get(link)
        try:
            login_zendesk = WebDriverWait(self.driver, TIMEOUT).until(
                EC.element_to_be_clickable((By.ID, 'user_email'))
            )
            login_zendesk.send_keys(self.usuario)

            pass_zendesk = self.driver.find_element(By.ID, 'user_password')
            pass_zendesk.send_keys(self.senha)

            entrar_zendesk = self.driver.find_element(By.ID, 'sign-in-submit-button')
            entrar_zendesk.click()
        except:
            pass

        WebDriverWait(self.driver, TIMEOUT).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-test-id="home_icon"]'))
        )


    def play(self, fila:int):
        self.driver.get(self.fila)
        play = WebDriverWait(self.driver, TIMEOUT).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-test-id="views_views-header-play-button"]'))
                )
        play.click()
        sleep(5)

    def fechar_dois_pacotes(self):
        try:
            dois_pacotes = WebDriverWait(self.driver, 30).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, 'header.modal-header a.close'))
                        )
            dois_pacotes.click()
            return True
        except:
            return False
        
    def selecionar_dropdown(self, id: int, valor_campo: str):
        seletor = f'[data-test-id="ticket-form-field-dropdown-field-{id}"] [data-garden-id="typography.ellipsis"]'
        campo = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, seletor))
        )
        campo.click()

        menu = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '[data-test-id="ticket-form-field-dropdown-menu"]'))
        )

        opcao = WebDriverWait(menu, 10).until(
            EC.element_to_be_clickable((By.XPATH, f'.//li[.//span[normalize-space()="{valor_campo}"]]'))
        )
        opcao.click()
    
    def obter_valores_input(self, ids:dict):
        valores_campos = {}
        for nome_campo, id_campo in ids.items():
            try:
                seletor = f'.custom_field_{id_campo} input[data-test-id="ticket-fields-text-field"]'
                elemento = self.driver.find_element(By.CSS_SELECTOR, seletor)
                valor_elemento = elemento.get_attribute("value")
                valores_campos[nome_campo] = valor_elemento

            except NoSuchElementException:
                print(f"Aviso: Campo com seletor '{seletor}' não foi encontrado.")
                valores_campos[nome_campo] = None
            
        return valores_campos
        
    def obter_valores_dropdown(self, ids:dict):
        valores_campos = {}
        for nome_campo, id_campo in ids.items():
            try:
                seletor = f'[data-test-id="ticket-form-field-dropdown-field-{id_campo}"] [data-garden-id="typography.ellipsis"]'
                elemento = self.driver.find_element(By.CSS_SELECTOR, seletor)
                valor_elemento = elemento.text
                valores_campos[nome_campo] = valor_elemento

            except NoSuchElementException:
                print(f"Aviso: Campo com seletor '{seletor}' não foi encontrado.")
                valores_campos[nome_campo] = None
        return valores_campos
        
    def preencher_input(self, id:int, valor:str):
        seletor = f'.custom_field_{id} input[data-test-id="ticket-fields-text-field"]'
        try:
            campo = self.driver.find_element(By.CSS_SELECTOR, seletor)
            campo.send_keys(valor)

        except NoSuchElementException:
            print(f"Aviso: Campo com seletor '{seletor}' não foi encontrado.")
            return None
        
    def enviar_aberto(self):
        actions = ActionChains(self.driver)
        actions.key_down(Keys.CONTROL).key_down(Keys.ALT).send_keys('o').key_up(Keys.ALT).key_up(Keys.CONTROL).perform()

    def fechar_ticket_atual(self):
        for i in range(3):
            try:
                fechar_ticket = WebDriverWait(self.driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-test-id="close-button"]'))
                )
                fechar_ticket.click()
                # fechar_aba = WebDriverWait(self.driver,10).until(
                #     EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-test-id="ticket-close-confirm-modal-confirm-btn"]'))
                # )
                # fechar_aba.click()
                print('Ticket fechado.')
                break
            except (StaleElementReferenceException, TimeoutException):
                print(f"Tentando fechar ticket.. Elemento obsoleto... (tentativa {i+1})")
                sleep(2)
    
    def esperar_carregamento(self):
        try:
            seletor_de_carregamento = (By.CSS_SELECTOR, "section.main_panes.ticket.working")
            
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located(seletor_de_carregamento)
            )
            WebDriverWait(self.driver, TIMEOUT).until(
                EC.invisibility_of_element_located(seletor_de_carregamento)
            )
            sleep(2)

        except TimeoutException:
            print("Nenhum círculo de carregamento detectado, continuando...")
            pass


class Zendesk_Zenpy:
    def __init__(self, zlogin, zpass, instancia):
        self.zlogin = zlogin
        self.zpass = zpass
        self.instancia = instancia
        self.zenpy_client = None
        self.auth_zenpy()


    def auth_zenpy(self):
        creds = {
            'email': self.zlogin,
            'token': self.zpass,
            'subdomain': self.instancia
        }
        try:
            print("Autenticando cliente Zenpy...")
            self.zenpy_client = Zenpy(session=session, **creds)
            print("Cliente Zenpy autenticado com sucesso.")
        except Exception as e:
            print(f"Erro na autenticação do Zenpy: {e}")

    def zenpy_client(self):
        return self.zenpy_client
            
    def pegar_tickets(self, fila:int, minimo=1):
        print('Verificando tickets na fila...')
        
        if not self.zenpy_client:
            print("Erro: Cliente Zenpy não foi autenticado. Verifique as credenciais.")
            return None
        
        todos_os_tickets = []
        try:
            for ticket in self.zenpy_client.views.tickets(view=fila):
                todos_os_tickets.append(ticket.id)
            if len(todos_os_tickets) >= minimo:
                print(f'A visualização conta com {len(todos_os_tickets)} tickets.')
                return todos_os_tickets
            else:
                print(f'A visualização não tem o minimo de tickets para inicializar. (Minimo: {minimo} Fila: {len(todos_os_tickets)})')
                return None
        except Exception as e:
            print(f"Erro ao buscar tickets: {str(e)}")
            return None
        
    def _valores_customfield(self, ticket: Any) -> Dict[int, Any]:
        
        if not hasattr(ticket, 'custom_fields') or not ticket.custom_fields:
            return {}

        field_objects: Iterable[Any]
        if hasattr(ticket.custom_fields, 'values'):
            field_objects = ticket.custom_fields.values()
        else:
            field_objects = ticket.custom_fields

        parsed_fields = {}
        for field in field_objects:
            field_id = None
            field_value = None

            if isinstance(field, dict):
                field_id = field.get('id')
                field_value = field.get('value')
            elif hasattr(field, 'id') and hasattr(field, 'value'):
                field_id = field.id
                field_value = field.value
            
            if field_id is not None:
                parsed_fields[field_id] = field_value
        
        return parsed_fields
    
    def extrair_customfields(self, ticket_id:int, lista_campos: Dict[str, int]) -> Optional[Dict[str, Any]]:
        try:
            ticket = self.zenpy_client.tickets(id=ticket_id)

            todos_os_valores = self._valores_customfield(ticket)

            resultado = {}
            for nome, id_campo in lista_campos.items():
                valor = todos_os_valores.get(id_campo)
                resultado[nome] = valor

            return resultado
        except RecordNotFoundException:
            print(f"Ticket {ticket_id} não encontrado no Zendesk.")
            return None
        except APIException as e:
            print(f"Erro de API ao buscar ticket {ticket_id}: {e}")
            return None
        except Exception:
            print(f"Erro inesperado ao processar ticket {ticket_id}:")
            traceback.print_exc()
            return None

#=============================================================================

