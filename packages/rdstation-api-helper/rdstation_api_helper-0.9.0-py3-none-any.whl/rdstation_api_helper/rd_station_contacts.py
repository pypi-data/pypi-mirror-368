# -------------------------------------------------------------------------------
# IMPORTS AND REQUIREMENTS
# -------------------------------------------------------------------------------

import json
import os
import pandas as pd
import random
import re
import requests
import time
import uuid
from urllib.parse import unquote

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    JSON,
    UUID,
    text,
)
from sqlalchemy import Table, MetaData, select
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()


def main():

    pgsql = PostgresDB()
    pgsql.create_tables()
    engine = pgsql.engine
    rd = RDStationAPI()

    # # 1. FETCH AND SAVE SEGMENTATIONS
    # json_data = rd.get_segmentations()
    # pgsql.save_to_sql(json_data, Segmentation, upsert_values=True)

    # # 2. FETCH AND SAVE SEGMENTATIONS CONTACTS
    # pattern_list = ["admissao", "admissão"]
    # segmentation_contacts = []

    # for name_pattern in pattern_list:
    #     segmentation_dict = filter_segmentations(engine, name_pattern)
    #     contact_data = rd.get_segmentation_contacts(segmentation_dict)
    #     segmentation_contacts.extend(contact_data)

    # pgsql.save_to_sql(segmentation_contacts, SegmentationContact, upsert_values=True)

    # # 3. FETCH AND UPDATE CONTACTS FUNNEL STATUS
    # df_1 = pd.read_sql_table('v_segmentation_contacts_unique', engine)
    # df_1 = df_1[['uuid']].astype(str)  # Ensure UUIDs are strings
    # print(f'The number of segmentation_contacts uuids is: {df_1.shape[0]}')

    # df_2 = pd.read_sql_table('rd_contact_funnel_status', engine)
    # df_2 = df_2[['uuid']].astype(str)  # Ensure UUIDs are strings
    # print(f'The number of contact_funnel_status uuids is: {df_2.shape[0]}')

    # # Get the difference between the two DataFrames
    # df_diff = df_1[~df_1['uuid'].isin(df_2['uuid'])]
    # print(f'The number of uuids in df_1 but not in df_2 is: {df_diff.shape[0]}')

    # contacts = df_diff.to_dict(orient='records')
    # funnel_status_data = rd.get_contacts_funnel_status(contacts)

    # pgsql.save_to_sql(funnel_status_data, ContactFunnelStatus, upsert_values=True)

    # # 4. FETCH AND UPDATE CONTACTS DATA
    # df_1 = pd.read_sql_table('v_segmentation_contacts_unique', engine)
    # df_1 = df_1[['uuid']].astype(str)  # Ensure UUIDs are strings
    # print(f'The number of segmentation_contacts uuids is: {df_1.shape[0]}')

    # df_2 = pd.read_sql_table('rd_contacts', engine)
    # df_2 = df_2[['uuid']].astype(str)  # Ensure UUIDs are strings
    # print(f'The number of contact_funnel_status uuids is: {df_2.shape[0]}')

    # # Get the difference between the two DataFrames
    # df_diff = df_1[~df_1['uuid'].isin(df_2['uuid'])]
    # print(f'The number of uuids in df_1 but not in df_2 is: {df_diff.shape[0]}')

    # contacts = df_diff.to_dict(orient='records')
    # contacts_data = rd.get_contacts_data(contacts)

    # pgsql.save_to_sql(contacts_data, Contact, upsert_values=True)

    # # 5. FETCH AND UPDATE EVENTS
    # df_1 = pd.read_sql_table('v_segmentation_contacts_unique', engine)
    # df_1 = df_1[['uuid']].astype(str)  # Ensure UUIDs are strings
    # print(f'The number of segmentation_contacts uuids is: {df_1.shape[0]}')

    # df_2 = pd.read_sql_table('rd_conversion_events', engine)
    # df_2 = df_2[['uuid']].astype(str)  # Ensure UUIDs are strings
    # print(f'The number of contact_funnel_status uuids is: {df_2.shape[0]}')

    # # Get the difference between the two DataFrames
    # df_diff = df_1[~df_1['uuid'].isin(df_2['uuid'])]
    # print(f'The number of uuids in df_1 but not in df_2 is: {df_diff.shape[0]}')

    # contacts = df_diff.to_dict(orient='records')
    # contacts_data = rd.get_contacts_events(contacts)

    # pgsql.save_to_sql(contacts_data, ConversionEvents, upsert_values=True)


# -------------------------------------------------------------------------------
# DEFINE THE SQLMODEL SCHEMA FOR TABLES
# -------------------------------------------------------------------------------

Base = declarative_base()


class Segmentation(Base):
    __tablename__ = "rd_segmentations"

    id = Column(String(50), primary_key=True)
    name = Column(String(255))
    standard = Column(Boolean)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    process_status = Column(String(50))
    links = Column(JSON, default=[])


class SegmentationContact(Base):
    __tablename__ = "rd_segmentation_contacts"

    uuid = Column(UUID, primary_key=True)
    name = Column(String(255))
    email = Column(String(255))
    last_conversion_date = Column(DateTime)
    created_at = Column(DateTime)
    links = Column(JSON, default=[])
    segmentation_id = Column(String(50), primary_key=True)
    segmentation_name = Column(String(255))
    unidade = Column(String(50))
    ano_interesse = Column(String(255))


class Contact(Base):
    __tablename__ = "rd_contacts"

    uuid = Column(String, primary_key=True)
    email = Column(String, nullable=False)
    name = Column(String, nullable=False)
    state = Column(String)
    city = Column(String)
    mobile_phone = Column(String)
    personal_phone = Column(String)
    tags = Column(JSON, default=[])
    legal_bases = Column(JSON, default=[])
    links = Column(JSON, default=[])
    conversion_events = Column(JSON, default=[])
    last_conversion_event = Column(String)
    unidade = Column(String)
    ano_interesse = Column(String)
    cf_1serie = Column(String)
    cf_ano_serie_admissao_bh = Column(String)
    cf_bernoulli_day_horario_de_preferencia = Column(String)
    cf_bgo_24_data_reun_p_24 = Column(String)
    cf_bgo_24_serie_de_intesesse_reun_p_24 = Column(String)
    cf_codigo = Column(String)
    cf_condicao_aprovada = Column(String)
    cf_cpf = Column(String)
    cf_curso = Column(String)
    cf_curso_que_deseja_cursar_na_universidade = Column(String)
    cf_ddd_whatsapp = Column(String)
    cf_desconto = Column(String)
    cf_desconto_0 = Column(String)
    cf_desconto_aplicado = Column(String)
    cf_desconto_final = Column(String)
    cf_e_a_primeira_vez_que_vai_fazer_enem = Column(String)
    cf_e_aluno_bernoulli = Column(String)
    cf_e_aluno_do_bernoulli = Column(String)
    cf_e_mail_responsavel_academico = Column(String)
    cf_e_mail_responsavel_financeiro = Column(String)
    cf_escola_onde_estuda_ou_estudou = Column(String)
    cf_escola_publica_ou_particular = Column(String)
    cf_form_url = Column(String)
    cf_growth_aluno_indicado = Column(String)
    cf_growth_e_mail_indicado = Column(String)
    cf_growth_evento_de_interesse_experience_2024_2 = Column(String)
    cf_growth_nome_do_aluno_bernoulli = Column(String)
    cf_growth_serie_de_interesse_lp = Column(String)
    cf_growth_tel_do_indicado = Column(String)
    cf_growth_vestibular_de_interesse = Column(String)
    cf_growth_vestibular_de_interesse_cascata = Column(String)
    cf_liberacao_rematricula = Column(String)
    cf_local_da_prova = Column(String)
    cf_local_de_oferta = Column(String)
    cf_matricula = Column(String)
    cf_matricula_0 = Column(String)
    cf_melhor_turno_para_visita = Column(String)
    cf_nome_do_aluno = Column(String)
    cf_nome_do_aluno_2 = Column(String)
    cf_nome_do_aluno_3 = Column(String)
    cf_nome_do_indicado_a_1 = Column(String)
    cf_nome_do_responsavel = Column(String)
    cf_nome_responsavel_reun_bgo = Column(String)
    cf_oferta_de_curso = Column(String)
    cf_origem = Column(String)
    cf_pab_25_growth_turma_de_interesse_2025_go = Column(String)
    cf_pab_25_growth_turma_de_interesse_2025_ssa = Column(String)
    cf_pab_25_growth_turma_de_interesse_2025_total = Column(String)
    cf_participou_da_prova_do_enem_em_algum_momento = Column(String)
    cf_podemos_confirmar_sua_presenca_no_simulado_bahiana = Column(String)
    cf_podemos_confirmar_sua_presenca_no_simulado_enem = Column(String)
    cf_pretende_comparecer_com_mais_1_acompanhante_alem_da_sua = Column(String)
    cf_processo = Column(String)
    cf_qual_o_curso_de_interesse = Column(String)
    cf_qual_o_seu_curso_de_interesse = Column(String)
    cf_ra = Column(String)
    cf_responsavel = Column(String)
    cf_responsavel_academico = Column(String)
    cf_responsavel_financeiro = Column(String)
    cf_rubeus = Column(String)
    cf_se_nao_e_aluno_de_qual_escola = Column(String)
    cf_serie_cursada_em_2024 = Column(String)
    cf_serie_de_interesse = Column(String)
    cf_serie_de_interesse_em_2025 = Column(String)
    cf_serie_s_de_interesse = Column(String)
    cf_site_contato_assunto = Column(String)
    cf_site_contato_mensagem = Column(String)
    cf_site_contato_unidade = Column(String)
    cf_site_politica_de_privacidade = Column(String)
    cf_site_pv_curso = Column(String)
    cf_temperatura_do_lead = Column(String)
    cf_turma_de_interesse = Column(String)
    cf_turno = Column(String)
    cf_unidade = Column(String)
    cf_unidade_de_interesse_em_2025 = Column(String)
    cf_valor_do_debito = Column(String)


class ContactFunnelStatus(Base):
    __tablename__ = "rd_contact_funnel_status"

    uuid = Column(UUID, primary_key=True)
    lifecycle_stage = Column(String(50))
    opportunity = Column(Boolean)
    contact_owner_email = Column(String(255))
    interest = Column(Integer)
    fit = Column(Integer)
    origin = Column(String(50))


class ConversionEvents(Base):
    __tablename__ = "rd_conversion_events"

    uuid = Column(UUID, primary_key=True)
    event_type = Column(String(50))
    event_family = Column(String(50))
    event_identifier = Column(String(255))
    event_timestamp = Column(DateTime)
    name = Column(String(255))
    email = Column(String(255))
    traffic_source = Column(String(255))
    tags = Column(JSON, default=[])
    cf_form_url = Column(String(255))


class Lead(Base):
    __tablename__ = "rd_leads"

    uuid = Column(UUID, primary_key=True)
    email = Column(String, primary_key=True)
    name = Column(String)
    unidade = Column(String)
    ano_interesse = Column(String, primary_key=True)
    tags = Column(JSON)


class PostgresDB:

    def __init__(self) -> None:
        self.db_host: str = os.getenv("DB_HOST")
        self.db_port: str = os.getenv("DB_PORT")
        self.db_user: str = os.getenv("DB_USER")
        self.db_pass: str = os.getenv("DB_PASS")
        self.db_name: str = os.getenv("DB_NAME")
        self.engine = self.create_engine()

    def create_engine(self) -> create_engine:
        uri: str = (
            f"postgresql+psycopg2://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}"
        )
        engine = create_engine(uri)
        return engine

    def create_tables(self) -> None:
        Base.metadata.create_all(self.engine)

    def save_to_sql(self, json_data: dict, model_class, upsert_values=False):

        print(f"Inserting data for {model_class.__name__}...")

        if not json_data:
            return

        df = pd.json_normalize(json_data, sep="_")

        allowed_keys = {c.name for c in model_class.__table__.columns}

        extra_keys = set(df.columns) - allowed_keys
        if extra_keys:
            print(f"Keys in json_data not in allowed_keys: {extra_keys}")

        bulk_data = [
            {k: v for k, v in row.items() if k in allowed_keys}
            for row in df.to_dict(orient="records")
        ]

        Session = sessionmaker(bind=self.engine)
        session = Session()

        try:
            if upsert_values:
                from sqlalchemy.dialects.postgresql import insert

                primary_keys = [key.name for key in model_class.__table__.primary_key]
                stmt = insert(model_class).values(bulk_data)
                stmt = stmt.on_conflict_do_update(
                    index_elements=primary_keys,
                    set_={
                        c.name: getattr(stmt.excluded, c.name)
                        for c in model_class.__table__.columns
                        if c.name not in primary_keys
                    },
                )
                session.execute(stmt)
            else:
                session.bulk_insert_mappings(model_class, bulk_data)
            session.commit()
            print(f"Data successfully inserted for {len(df)} items.")

        except Exception as e:
            session.rollback()
            print(f"An error occurred: {e}")

        finally:
            session.close()


class RDStationAPI:
    """Functions to query RD Station API endpoints"""

    def __init__(self):
        self.RD_CLIENT_ID = os.getenv("RDSTATION_CLIENT_ID")
        self.RD_CLIENT_SECRET = os.getenv("RDSTATION_CLIENT_SECRET")
        self.RD_REFRESH_TOKEN = os.getenv("RDSTATION_REFRESH_TOKEN")
        self.RD_API_TOKEN = self.get_refresh_token()

    def get_refresh_token(self) -> str:
        url = "https://api.rd.services/auth/token"
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        data = {
            "client_id": self.RD_CLIENT_ID,
            "client_secret": self.RD_CLIENT_SECRET,
            "refresh_token": self.RD_REFRESH_TOKEN,
            "grant_type": "refresh_token",
        }

        response = requests.post(url, headers=headers, json=data)

        if response.status_code == 200:
            return response.json().get("access_token")

        print(f"Error: {response.status_code}")
        return None

    def get_segmentations(self, save_json_file: bool = False) -> dict:

        print("Fetching segmentations...")

        url = "https://api.rd.services/platform/segmentations"
        params = {"page": 1, "page_size": 100}
        headers = {"Authorization": f"Bearer {self.RD_API_TOKEN}"}

        all_results = []

        while True:
            response = requests.get(url, headers=headers, params=params)

            if response.status_code != 200:
                print(f"Error: {response.status_code}")
                break

            data = response.json()
            segmentations = data.get("segmentations", [])
            num_items = len(segmentations)

            print(f"Page {params['page']} - Found {num_items} items")

            # Add current page's data to the results
            all_results.extend(segmentations)

            params["page"] += 1  # Increment the page number

            if num_items < 100:  # Break if no items was less than a full page
                break

        print(f"Fetched {len(all_results)} total items.")

        if save_json_file:
            # Save all results to a local JSON file
            with open("rd_segmentations.json", "w", encoding="utf-8") as json_file:
                json.dump(
                    all_results, json_file, indent=4, ensure_ascii=False, default=str
                )

            print("Data saved to `rd_segmentations.json`")

            df = pd.DataFrame(all_results)
            df.to_csv("rd_segmentations.csv", index=False)

            print("Data saved to `rd_segmentations.csv`")

        return all_results

    def get_segmentation_contacts(
        self, segmentation_dict: dict, save_json_file: bool = False
    ) -> dict:
        dict_count = 0
        dict_length = len(segmentation_dict)

        all_results = []

        for item in segmentation_dict:

            dict_count += 1

            segmentation_id = item["segmentation_id"]
            segmentation_name = item["segmentation_name"]

            url = f"https://api.rd.services/platform/segmentations/{segmentation_id}/contacts"
            params = {"page": 1, "page_size": 100, "order": "last_conversion_date"}
            headers = {"Authorization": f"Bearer {self.RD_API_TOKEN}"}

            while True:
                response = requests.get(url, headers=headers, params=params)

                if response.status_code != 200:
                    print(f"Error: {response.status_code}")
                    break

                data = response.json()

                contacts = data.get("contacts", [])
                num_items = len(contacts)

                print(
                    f"{dict_count}/{dict_length} - {segmentation_name}, p.{params['page']}, found {num_items} items"
                )

                # Append segmentation_id and segmentation_name to each contact
                for contact in contacts:
                    contact["segmentation_id"] = segmentation_id
                    contact["segmentation_name"] = segmentation_name

                # Add current page's data to the results
                all_results.extend(contacts)

                params["page"] += 1  # Increment the page number

                if num_items < 100:  # Break if no items was less than a full page
                    break

                # Sleep for 0.5 seconds to respect 2 requests per second
                time.sleep(1 / 2)

        print(f"Fetched {len(all_results)} total items.")

        df = pd.DataFrame(all_results)

        df["unidade"] = df["segmentation_name"].apply(
            lambda seg: next(
                (
                    u
                    for u in self.classify_value(seg, self.unidade_mapping)
                    if u is not None
                ),
                None,
            )
        )
        df["ano_interesse"] = df["segmentation_name"].apply(
            lambda seg: next(
                (
                    i
                    for i in self.classify_value(seg, self.interesse_mapping)
                    if i is not None
                ),
                None,
            )
        )

        all_results = df.to_dict(orient="records")

        if save_json_file:
            # Save all results to a local JSON file
            with open(
                "rd_segmentation_contacts.json", "w", encoding="utf-8"
            ) as json_file:
                json.dump(
                    all_results, json_file, indent=4, ensure_ascii=False, default=str
                )

            print("Data saved to `rd_segmentation_contacts.json`")

        return all_results

    def get_contact_data(self, uuid_value: str, max_retries: int = 3) -> dict:
        """Fetch a single contact data with retry handling."""

        url = f"https://api.rd.services/platform/contacts/{uuid_value}"
        headers = {"Authorization": f"Bearer {self.RD_API_TOKEN}"}

        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers)

                # Handle successful request
                if response.status_code == 200:
                    return response.json()

                # Handle Rate Limiting (429 Too Many Requests)
                elif response.status_code == 429:
                    wait_time = 20
                    print(
                        f"Rate limited for {uuid_value}. Retrying in {wait_time:.2f}s..."
                    )
                    time.sleep(wait_time)

                # Handle Server Errors (500-599)
                elif 500 <= response.status_code < 600:
                    wait_time = 2**attempt + random.uniform(0, 1)
                    print(
                        f"Server error {response.status_code} for {uuid_value}. Retrying in {wait_time:.2f}s..."
                    )
                    time.sleep(wait_time)

                else:
                    print(
                        f"Failed to fetch {uuid_value}, HTTP {response.status_code}. Skipping."
                    )
                    break  # Skip this item after retries

            except requests.exceptions.RequestException as e:
                print(f"Request failed for {uuid_value}: {e}. Retrying...")
                # Exponential backoff on connection errors
                time.sleep(2**attempt)

        print(f"Max retries exceeded for {uuid_value}. Giving up.")
        return None

    def get_contacts_data(
        self, contact_dict: list, batch_size: int = 500, save_json_file: bool = False
    ) -> dict:
        """Fetch contact data sequentially for a list of contacts."""
        item_count = 0
        dict_length = len(contact_dict)

        all_results = []

        # Iterate over the contacts in batches of 500

        for batch in self.process_in_batches(contact_dict, batch_size):
            batch_results = []

            for item in batch:
                uuid_value = str(item["uuid"])  # Ensure UUID is a string

                response = self.get_contact_data(uuid_value)
                if not response["uuid"]:
                    continue

                batch_results.append(response)

                item_count += 1
                print(f"{item_count}/{dict_length} - fetched contact {uuid_value}")

                # Respect API rate limit (120 requests/min → 1 request per 0.5 sec)
                time.sleep(0.5)

            all_results.extend(batch_results)

        for contact in all_results:
            contact["unidade"] = None
            contact["ano_interesse"] = None

            unidades = []
            cf_unidade = contact.get("cf_unidade")
            cf_unidade_de_interesse_em_2025 = contact.get(
                "cf_unidade_de_interesse_em_2025"
            )
            cf_unidades = [cf_unidade, cf_unidade_de_interesse_em_2025]

            interesses = []
            cf_serie_de_interesse = contact.get("cf_serie_de_interesse")
            cf_serie_de_interesse_em_2025 = contact.get("cf_serie_de_interesse_em_2025")
            cf_serie_s_de_interesse = contact.get("cf_serie_s_de_interesse")
            cf_turma_de_interesse = contact.get("cf_turma_de_interesse")
            cf_anos_series_turmas = [
                cf_serie_de_interesse,
                cf_serie_de_interesse_em_2025,
                cf_serie_s_de_interesse,
                cf_turma_de_interesse,
            ]  # noqa: E501

            tags = contact.get("tags", [])

            for value in cf_unidades:
                unidades.extend(self.classify_value(value, self.unidade_mapping))

            for value in cf_anos_series_turmas:
                interesses.extend(self.classify_value(value, self.interesse_mapping))

            for tag in tags:
                unidades.extend(self.classify_value(tag, self.unidade_mapping))
                interesses.extend(self.classify_value(tag, self.interesse_mapping))

            valid_unidades = [u for u in unidades if u is not None]
            contact["unidade"] = valid_unidades[0] if valid_unidades else None

            valid_interesses = [i for i in interesses if i is not None]
            contact["ano_interesse"] = valid_interesses[0] if valid_interesses else None

            # Save to JSON if requested
            if save_json_file:
                append_to_json_file("rd_contacts_data.json", batch_results)

        print(f"Fetched {len(all_results)} total items.")
        return all_results

    def get_contact_funnel_status(self, uuid_value: str, max_retries: int = 3) -> dict:
        """Fetch a single contact funnel status with retry handling."""

        url = f"https://api.rd.services/platform/contacts/{uuid_value}/funnels/default"
        headers = {"Authorization": f"Bearer {self.RD_API_TOKEN}"}

        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers)

                # Handle successful request
                if response.status_code == 200:
                    return response.json()

                # Handle Rate Limiting (429 Too Many Requests)
                elif response.status_code == 429:
                    wait_time = 20
                    print(
                        f"Rate limited for {uuid_value}. Retrying in {wait_time:.2f}s..."
                    )
                    time.sleep(wait_time)

                # Handle Server Errors (500-599)
                elif 500 <= response.status_code < 600:
                    wait_time = 2**attempt + random.uniform(0, 1)
                    print(
                        f"Server error {response.status_code} for {uuid_value}. Retrying in {wait_time:.2f}s..."
                    )
                    time.sleep(wait_time)

                else:
                    print(
                        f"Failed to fetch {uuid_value}, HTTP {response.status_code}. Skipping."
                    )
                    break  # Skip this item after retries

            except requests.exceptions.RequestException as e:
                print(f"Request failed for {uuid_value}: {e}. Retrying...")
                # Exponential backoff on connection errors
                time.sleep(2**attempt)

        print(f"Max retries exceeded for {uuid_value}. Giving up.")
        return None

    def get_contacts_funnel_status(
        self, contact_dict: list, batch_size: int = 500, save_json_file: bool = False
    ) -> dict:  # noqa: E501
        """Fetch contact funnel status sequentially for a list of contacts."""
        item_count = 0
        dict_length = len(contact_dict)

        all_results = []

        # Iterate over the contacts in batches of 500

        for batch in self.process_in_batches(contact_dict, batch_size):
            batch_results = []

            for item in batch:
                uuid_value = str(item["uuid"])  # Ensure UUID is a string

                response = self.get_contact_funnel_status(uuid_value)
                if not response:
                    continue

                response["uuid"] = uuid_value
                batch_results.append(response)

                item_count += 1
                print(f"{item_count}/{dict_length} - fetched contact {uuid_value}")

                # Respect API rate limit (120 requests/sec → 1 request per 0.5 sec)
                time.sleep(0.5)

            all_results.extend(batch_results)

            # Save to JSON if requested
            if save_json_file:
                append_to_json_file("rd_contacts_funnel_status.json", batch_results)

        print(f"Fetched {len(all_results)} total items.")
        return all_results

    def get_contact_events(self, uuid_value: str, max_retries: int = 3) -> dict:
        """Fetch a single contact funnel status with retry handling."""

        url = f"https://api.rd.services/platform/contacts/{uuid_value}/events?event_type=CONVERSION"
        headers = {"Authorization": f"Bearer {self.RD_API_TOKEN}"}

        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers)

                # Handle successful request
                if response.status_code == 200:
                    return response.json()

                # Handle Rate Limiting (429 Too Many Requests)
                elif response.status_code == 429:
                    wait_time = 20
                    print(
                        f"Rate limited for {uuid_value}. Retrying in {wait_time:.2f}s..."
                    )
                    time.sleep(wait_time)

                # Handle Server Errors (500-599)
                elif 500 <= response.status_code < 600:
                    wait_time = 2**attempt + random.uniform(0, 1)
                    print(
                        f"Server error {response.status_code} for {uuid_value}. Retrying in {wait_time:.2f}s..."
                    )
                    time.sleep(wait_time)

                else:
                    print(
                        f"Failed to fetch {uuid_value}, HTTP {response.status_code}. Skipping."
                    )
                    break  # Skip this item after retries

            except requests.exceptions.RequestException as e:
                print(f"Request failed for {uuid_value}: {e}. Retrying...")
                # Exponential backoff on connection errors
                time.sleep(2**attempt)

        print(f"Max retries exceeded for {uuid_value}. Giving up.")
        return None

    def get_contacts_events(
        self, contact_dict: list, batch_size: int = 500, save_json_file: bool = False
    ) -> dict:  # noqa: E501
        """Fetch contact funnel status sequentially for a list of contacts."""
        item_count = 0
        dict_length = len(contact_dict)

        all_results = []

        # Iterate over the contacts in batches of 500

        for batch in self.process_in_batches(contact_dict, batch_size):
            batch_results = []

            for item in batch:
                uuid_value = str(item["uuid"])  # Ensure UUID is a string

                response = self.get_contact_events(uuid_value)
                if not response:
                    continue

                for value in response:
                    tags = value.get("payload", {}).get("tags")

                    for tag in tags:
                        unidades = self.classify_value(tag, self.unidade_mapping)
                        interesses = self.classify_value(tag, self.interesse_mapping)

                    valid_unidades = [u for u in unidades if u is not None]
                    unidade = valid_unidades[0] if valid_unidades else None

                    valid_interesses = [i for i in interesses if i is not None]
                    ano_interesse = valid_interesses[0] if valid_interesses else None

                    event = {
                        "uuid": uuid_value,
                        "event_type": value.get("event_type"),
                        "event_family": value.get("event_family"),
                        "event_identifier": value.get("event_identifier"),
                        "event_timestamp": value.get("event_timestamp"),
                        "name": value.get("payload", {}).get("name"),
                        "email": value.get("payload", {}).get("email"),
                        "traffic_source": value.get("payload", {}).get(
                            "traffic_source"
                        ),
                        "tags": value.get("payload", {}).get("tags"),
                        "cf_form_url": value.get("payload", {}).get("cf_form_url"),
                        "unidade": unidade,
                        "ano_interesse": ano_interesse,
                    }

                    batch_results.append(event)

                item_count += 1
                print(
                    f"{item_count}/{dict_length} - fetched events for contact {uuid_value}"
                )

                # Respect API rate limit (120 requests/sec → 1 request per 0.5 sec)
                time.sleep(0.5)

            all_results.extend(batch_results)

            # Save to JSON if requested
            if save_json_file:
                append_to_json_file("rd_conversion_events.json", batch_results)

        print(f"Fetched {len(all_results)} total items.")
        return all_results

    @staticmethod
    def process_in_batches(all_data: list, batch_size=500):
        # Generator to yield batches of contacts
        for i in range(0, len(all_data), batch_size):
            yield all_data[i : i + batch_size]

    @staticmethod
    def decode_if_needed(text_string: str) -> str:
        """
        Decodes a string that may be encoded with percent-encoding and/or Unicode escape sequences.

        Parameters:
            text_string (str): The input string that may be encoded.

        Returns:
            str: The fully decoded string.
        """
        # Decode percent-encoded sequences if present.
        if re.search(r"%[0-9A-Fa-f]{2}", text_string):
            text_string = unquote(text_string)

        # Decode Unicode escapes if the literal "\u" is found.
        if "\\u" in text_string:
            try:
                text_string = text_string.encode("utf-8").decode(
                    "unicode_escape"
                )  # noqa: W605
            except Exception as e:
                print("Unicode escape decoding failed:", e)

        return text_string

    def classify_value(self, value: str, mapping: dict) -> list:
        """
        Processes a single string value:

        Parameters:
            value (str): The input string to classify.
            mapping (dict): A dictionary where keys are classification labels and values are regex strings.

        Returns:
            list: A list of classification labels that match the input value.
        """
        if value == "" or value is None:
            return []

        # Step 1: Decode the string.
        decoded_value = self.decode_if_needed(value)

        # Step 2: Normalize the string.
        normalized_value = decoded_value.strip().lower()

        # Step 3: Remove any "admissao" or "admissão" occurrences.
        normalized_value = re.sub(r"admiss[aã]o", "", normalized_value)

        matches = []
        # Step 4: Iterate over the mapping and search using the provided regex patterns.
        for key, regex_pattern in mapping.items():
            if re.search(regex_pattern, normalized_value, re.IGNORECASE):
                matches.append(key)

        return matches

    unidade_mapping = {
        "BH": r"(?:belo horizonte|bh)",
        "VSE": r"(?:nova lima|vale do sereno|nl|vse)",
        "CDA": r"(?:salvador|ssa|cda)",
        "MOD": r"(?:m[oó]dulo)",
    }

    interesse_mapping = {
        "Ensino Infantil - 1º período": r"(?=.*\binfantil\b)(?=.*\b1(?:º|ª|a|o|-)\b)(?=.*\b(?:s[eé]rie|ano|per[ií]odo)\b).*",  # noqa: E501
        "Ensino Infantil - 2º período": r"(?=.*\binfantil\b)(?=.*\b2(?:º|ª|a|o|-)\b)(?=.*\b(?:s[eé]rie|ano|per[ií]odo)\b).*",  # noqa: E501
        "Ensino Fundamental - 1º ano": r"(?=.*\bfundamental\b)(?=.*\b1(?:º|ª|a|o|-)\b)(?=.*\b(?:s[eé]rie|ano|per[ií]odo)\b).*",  # noqa: E501
        "Ensino Fundamental - 2º ano": r"(?=.*\bfundamental\b)(?=.*\b2(?:º|ª|a|o|-)\b)(?=.*\b(?:s[eé]rie|ano|per[ií]odo)\b).*",  # noqa: E501
        "Ensino Fundamental - 3º ano": r"(?=.*\bfundamental\b)(?=.*\b3(?:º|ª|a|o|-)\b)(?=.*\b(?:s[eé]rie|ano|per[ií]odo)\b).*",  # noqa: E501
        "Ensino Fundamental - 4º ano": r"(?=.*\bfundamental\b)(?=.*\b4(?:º|ª|a|o|-)\b)(?=.*\b(?:s[eé]rie|ano|per[ií]odo)\b).*",  # noqa: E501
        "Ensino Fundamental - 5º ano": r"(?=.*\bfundamental\b)(?=.*\b5(?:º|ª|a|o|-)\b)(?=.*\b(?:s[eé]rie|ano|per[ií]odo)\b).*",  # noqa: E501
        "Ensino Fundamental - 6º ano": r"(?=.*\bfundamental\b)(?=.*\b6(?:º|ª|a|o|-)\b)(?=.*\b(?:s[eé]rie|ano|per[ií]odo)\b).*",  # noqa: E501
        "Ensino Fundamental - 7º ano": r"(?=.*\bfundamental\b)(?=.*\b7(?:º|ª|a|o|-)\b)(?=.*\b(?:s[eé]rie|ano|per[ií]odo)\b).*",  # noqa: E501
        "Ensino Fundamental - 8º ano": r"(?=.*\bfundamental\b)(?=.*\b8(?:º|ª|a|o|-)\b)(?=.*\b(?:s[eé]rie|ano|per[ií]odo)\b).*",  # noqa: E501
        "Ensino Fundamental - 9º ano": r"(?=.*\bfundamental\b)(?=.*\b9(?:º|ª|a|o|-)\b)(?=.*\b(?:s[eé]rie|ano|per[ií]odo)\b).*",  # noqa: E501
        "Ensino Médio - 1ª série": r"(?=.*\bm[eé]dio\b)(?=.*\b1(?:º|ª|a|o|-)\b)(?=.*\b(?:s[eé]rie|ano|per[ií]odo)\b).*",  # noqa: E501
        "Ensino Médio - 2ª série": r"(?=.*\bm[eé]dio\b)(?=.*\b2(?:º|ª|a|o|-)\b)(?=.*\b(?:s[eé]rie|ano|per[ií]odo)\b).*",  # noqa: E501
        "Ensino Médio - 3ª série": r"(?=.*\bm[eé]dio\b)(?=.*\b3(?:º|ª|a|o|-)\b)(?=.*\b(?:s[eé]rie|ano|per[ií]odo)\b).*",  # noqa: E501
    }


# -------------------------------------------------------------------------------
# FUNCTIONS TO MANIPULATE DATA
# -------------------------------------------------------------------------------


def append_to_json_file(file_path, json_data):
    try:
        if os.path.exists(file_path):
            with open(file_path, "r+", encoding="utf-8") as f:

                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    print(
                        "JSON decode error: File is empty or invalid. Aborting operation."
                    )
                    return

                if not isinstance(data, list):
                    print("Existing JSON structure is not a list. Aborting operation.")
                    return
                print(f"Found {len(data)} records in the file.")

                if isinstance(json_data, list):
                    data.extend(json_data)
                    print(f"Appending {len(json_data)} record(s).")

                else:
                    data.append(json_data)
                    print("Appending 1 record.")

                f.seek(0)
                json.dump(data, f, indent=2)
                f.truncate()
            print(
                f"Records [{len(data):,}] appended successfully to file `{file_path}`."
            )

        else:
            with open(file_path, "w", encoding="utf-8") as f:
                if isinstance(json_data, list):
                    data = json_data
                    print(
                        f"Creating new file `{file_path}` and adding {len(json_data)} record(s)."
                    )
                else:
                    data = [json_data]
                    print(f"Creating new `{file_path}` file and adding 1 record.")
                json.dump(data, f, indent=2)
            print("File created and records added successfully.")

    except Exception as e:
        print("An error occurred:", e)


def filter_segmentations(engine, name_pattern: str = None) -> dict:
    # Create a session
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Set default pattern if name_pattern is None
        name_pattern = "%adm%" if name_pattern is None else f"%{name_pattern.lower()}%"

        query = text(
            'SELECT id, "name" FROM rd_segmentations WHERE lower("name") LIKE :name_pattern'
        )

        result = session.execute(query, {"name_pattern": name_pattern})

        segmentation_dict = [
            {"segmentation_id": row["id"], "segmentation_name": row["name"]}
            for row in result.mappings()
        ]

    finally:
        session.close()

    return segmentation_dict


def get_unique_segmentation_contacts(engine, name_pattern: str = None) -> list:
    """Fetch unique contacts from the database efficiently."""
    Session = sessionmaker(bind=engine)
    session = Session()

    # Define the table dynamically
    metadata = MetaData()
    table = Table("rd_segmentation_contacts", metadata, autoload_with=engine)

    try:
        # Use a faster search method instead of LOWER()
        name_pattern = "%" if name_pattern is None else f"%{name_pattern}%"

        # Properly reference table columns instead of raw strings
        query = (
            select(table.c.uuid, table.c.email)
            .distinct()
            .where(
                table.c.segmentation_name.ilike(name_pattern)  # Case-insensitive search
            )
        )

        result = session.execute(query)
        unique_contacts = [
            {"uuid": row.uuid, "email": row.email} for row in result.fetchall()
        ]

    finally:
        session.close()

    print(f"Query returned {len(unique_contacts):,} unique contacts.")

    return unique_contacts


# -------------------------------------------------------------------------------
# AUXILIAR FUNCTIONS
# -------------------------------------------------------------------------------


def calculate_unique_contacts():

    pgsql = PostgresDB()
    pgsql.create_tables()
    engine = pgsql.engine
    rd = RDStationAPI()

    # # Read table 'rd_contacts' and save its data as a local JSON file
    # df_contacts = pd.read_sql_table("rd_contacts", engine)
    # contacts_data = df_contacts.to_dict(orient="records")

    # # Convert UUID objects to strings
    # for contact in contacts_data:
    #     if "uuid" in contact and isinstance(contact["uuid"], uuid.UUID):
    #         contact["uuid"] = str(contact["uuid"])

    # with open('rd_contacts_data.json', 'w', encoding='utf-8') as json_file:
    #     json.dump(contacts_data, json_file, indent=4, ensure_ascii=False)

    # print("Data from 'rd_contacts' table saved to 'rd_contacts_data.json'")

    # Read JSON file 'rd_contacts_data' calculate unidade and ano_interesse

    with open("rd_contacts_data.json.bkp", "r", encoding="utf-8") as f:
        contacts_data = json.load(f)

    leads = []

    for item in contacts_data:
        item["unidade"] = None
        item["ano_interesse"] = None

        unidades = []
        cf_unidade = item.get("cf_unidade")
        cf_unidade_de_interesse_em_2025 = item.get("cf_unidade_de_interesse_em_2025")
        cf_unidades = [cf_unidade, cf_unidade_de_interesse_em_2025]

        interesses = []
        cf_serie_de_interesse = item.get("cf_serie_de_interesse")
        cf_serie_de_interesse_em_2025 = item.get("cf_serie_de_interesse_em_2025")
        cf_serie_s_de_interesse = item.get("cf_serie_s_de_interesse")
        cf_turma_de_interesse = item.get("cf_turma_de_interesse")
        cf_anos_series_turmas = [
            cf_serie_de_interesse,
            cf_serie_de_interesse_em_2025,
            cf_serie_s_de_interesse,
            cf_turma_de_interesse,
        ]  # noqa: E501

        tags = item.get("tags", [])

        for value in cf_unidades:
            unidades.extend(rd.classify_value(value, rd.unidade_mapping))

        for value in cf_anos_series_turmas:
            interesses.extend(rd.classify_value(value, rd.interesse_mapping))

        for tag in tags:
            unidades.extend(rd.classify_value(tag, rd.unidade_mapping))
            interesses.extend(rd.classify_value(tag, rd.interesse_mapping))

        # Select first unidade value
        valid_unidades = [u for u in unidades if u is not None]
        if valid_unidades:
            item["unidade"] = valid_unidades[0]

        # Remove duplicates and None values
        valid_interesses = list({i for i in interesses if i is not None})

        flattened_item_list = [
            {**item, "ano_interesse": tag if tag else None}
            for tag in (
                valid_interesses
                if isinstance(valid_interesses, list)
                else [valid_interesses] if valid_interesses else [None]
            )
        ]

        for item in flattened_item_list:
            lead = {
                "uuid": item["uuid"],
                "email": item["email"],
                "name": item["name"],
                "unidade": item["unidade"],
                "ano_interesse": item["ano_interesse"],
                "tags": item["tags"],
            }

            leads.append(lead)

    # with open("rd_leads.json", "w", encoding="utf-8") as f:
    #     json.dump(leads, f, indent=4, ensure_ascii=False)

    pgsql.save_to_sql(leads, Lead, upsert_values=True)


# -------------------------------------------------------------------------------
# OTHER FUNCTIONS
# -------------------------------------------------------------------------------

# # List all different possible keys in all items from data
# all_keys = set()
# for item in data:
#     if item is None:
#         continue
#     all_keys.update(item.keys())

# print('The different possible keys in all items from the JSON object are:')
# for key in all_keys:
#     print(key)


def fix_contacts_data():

    pgsql = PostgresDB()
    engine = pgsql.engine
    rd = RDStationAPI()

    # Read table 'rd_contacts' and save its data as a local JSON file
    df_contacts = pd.read_sql_table("rd_contacts", engine)
    contacts_data = df_contacts.to_dict(orient="records")

    for contact in contacts_data:
        contact["unidade"] = None
        contact["ano_interesse"] = None

        unidades = []
        cf_unidade = contact.get("cf_unidade")
        cf_unidade_de_interesse_em_2025 = contact.get("cf_unidade_de_interesse_em_2025")
        cf_unidades = [cf_unidade, cf_unidade_de_interesse_em_2025]

        interesses = []
        cf_serie_de_interesse = contact.get("cf_serie_de_interesse")
        cf_serie_de_interesse_em_2025 = contact.get("cf_serie_de_interesse_em_2025")
        cf_serie_s_de_interesse = contact.get("cf_serie_s_de_interesse")
        cf_turma_de_interesse = contact.get("cf_turma_de_interesse")
        cf_anos_series_turmas = [
            cf_serie_de_interesse,
            cf_serie_de_interesse_em_2025,
            cf_serie_s_de_interesse,
            cf_turma_de_interesse,
        ]  # noqa: E501

        tags = contact.get("tags", [])

        for value in cf_unidades:
            unidades.extend(rd.classify_value(value, rd.unidade_mapping))

        for value in cf_anos_series_turmas:
            interesses.extend(rd.classify_value(value, rd.interesse_mapping))

        for tag in tags:
            unidades.extend(rd.classify_value(tag, rd.unidade_mapping))
            interesses.extend(rd.classify_value(tag, rd.interesse_mapping))

        valid_unidades = [u for u in unidades if u is not None]
        if valid_unidades:
            contact["unidade"] = valid_unidades[0]

        valid_interesses = [i for i in interesses if i is not None]
        if valid_interesses:
            contact["ano_interesse"] = valid_interesses[0]

    with open("rd_contacts_data.json", "w", encoding="utf-8") as f:
        json.dump(contacts_data, f, indent=4, ensure_ascii=False)

    pgsql.save_to_sql(contacts_data, Contact, upsert_values=True)


def fix_segmentation_contacts():

    pgsql = PostgresDB()
    engine = pgsql.engine
    rd = RDStationAPI()

    # Read table 'rd_contacts', calculate unidade and ano_interesse and save it as a local JSON file
    df = pd.read_sql_table("rd_segmentation_contacts", engine)

    df["unidade"] = df["segmentation_name"].apply(
        lambda seg: next(
            (u for u in rd.classify_value(seg, rd.unidade_mapping) if u is not None),
            None,
        )
    )
    df["ano_interesse"] = df["segmentation_name"].apply(
        lambda seg: next(
            (i for i in rd.classify_value(seg, rd.interesse_mapping) if i is not None),
            None,
        )
    )

    contacts_data = df.to_dict(orient="records")

    with open("rd_segmentation_contacts.json", "w", encoding="utf-8") as f:
        json.dump(contacts_data, f, indent=4, ensure_ascii=False, default=str)

    pgsql.save_to_sql(contacts_data, SegmentationContact, upsert_values=True)


def fix_conversion_events():

    pgsql = PostgresDB()
    engine = pgsql.engine
    rd = RDStationAPI()

    # Read table 'rd_contacts' and save its data as a local JSON file
    df = pd.read_sql_table("rd_conversion_events", engine)
    events_data = df.to_dict(orient="records")

    for event in events_data:
        event["unidade"] = None
        event["ano_interesse"] = None
        tags = event.get("tags", [])

        for tag in tags:
            unidades = rd.classify_value(tag, rd.unidade_mapping)
            interesses = rd.classify_value(tag, rd.interesse_mapping)

        valid_unidades = [u for u in unidades if u is not None]
        event["unidade"] = valid_unidades[0] if valid_unidades else None

        valid_interesses = [i for i in interesses if i is not None]
        event["ano_interesse"] = valid_interesses[0] if valid_interesses else None

    with open("rd_contacts_data.json", "w", encoding="utf-8") as f:
        json.dump(events_data, f, indent=4, ensure_ascii=False)

    pgsql.save_to_sql(events_data, ConversionEvents, upsert_values=True)


def save_backup_files():

    # SET UP THE POSTGRESQL CONNECTION AND SESSION
    engine = PostgresDB.create_engine()
    PostgresDB.create_tables(engine)

    df = pd.read_sql_table("rd_segmentations", engine)
    data = df.to_dict(orient="records")
    with open("rd_segmentations.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False, default=str)

    df = pd.read_sql_table("rd_segmentation_contacts", engine)
    data = df.to_dict(orient="records")
    with open("rd_segmentation_contacts.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False, default=str)

    df = pd.read_sql_table("rd_contacts", engine)
    data = df.to_dict(orient="records")
    with open("rd_contacts.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False, default=str)

    df = pd.read_sql_table("rd_contact_funnel_status", engine)
    data = df.to_dict(orient="records")
    with open("rd_contact_funnel_status.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False, default=str)


if __name__ == "__main__":
    calculate_unique_contacts()
