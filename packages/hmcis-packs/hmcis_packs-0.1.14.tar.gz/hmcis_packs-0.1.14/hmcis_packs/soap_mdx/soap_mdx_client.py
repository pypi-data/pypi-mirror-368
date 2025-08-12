# -*- coding: utf-8 -*-
from __future__ import annotations

import re
import threading
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
from xml.sax.saxutils import escape

import pandas as pd
import requests
import yaml
from jinja2 import Template

pd.options.display.width = 1000
pd.options.display.max_columns = 1000
pd.options.display.max_rows = 1000


# ----------------------------------------------------------------------
# Вспомогательные типы
# ----------------------------------------------------------------------
@dataclass(frozen=True)
class _DimSpec:
    """Внутренняя нормализованная спецификация измерения."""
    dimension: str
    hierarchy: str
    level: str
    attributes: Optional[List[str]]
    dim_unique: str  # уже в квадратных скобках


# ----------------------------------------------------------------------
# Клиент XMLA → SAP BW
# ----------------------------------------------------------------------
class SAPXMLAClient:
    """
    Лёгкий клиент для SAP BW по XMLA:
      - Discover (dimensions, members, properties, levels)
      - Execute MDX (Tabular/AxisFormat=Tuple)
      - Хелперы для выборки членов с атрибутами (single/multi, batching)

    Важно: реализация счётчика в execute_mdx НЕ тронута.
    """

    DISCOVER_TEMPLATE = Template("""
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                      xmlns:xmla="urn:schemas-microsoft-com:xml-analysis">
      <soapenv:Header/>
      <soapenv:Body>
        <xmla:Discover>
          <xmla:RequestType>{{ request_type }}</xmla:RequestType>
          <xmla:Restrictions>
            <xmla:RestrictionList>
              {% for key, value in restrictions.items() %}
              <xmla:{{ key }}>{{ value }}</xmla:{{ key }}>
              {% endfor %}
            </xmla:RestrictionList>
          </xmla:Restrictions>
          <xmla:Properties>
            <xmla:PropertyList>
              <xmla:Catalog>{{ catalog }}</xmla:Catalog>
              <xmla:DataSourceInfo>{{ datasource }}</xmla:DataSourceInfo>
              <xmla:Format>{{ format_type }}</xmla:Format>
              {% for key, value in extra_properties.items() %}
              <xmla:{{ key }}>{{ value }}</xmla:{{ key }}>
              {% endfor %}
            </xmla:PropertyList>
          </xmla:Properties>
        </xmla:Discover>
      </soapenv:Body>
    </soapenv:Envelope>
    """)

    # ------------------------ ctor / transport -------------------------

    def __init__(self, url: str, username: str, password: str,
                 catalog: str = "$INFOCUBE", datasource: str = "SAP_BW"):
        self.url = url
        self.auth = (username, password)
        self.catalog = catalog
        self.datasource = datasource
        self.ns = {'x': 'urn:schemas-microsoft-com:xml-analysis:rowset'}

    def _send(self, soap_body: str, soap_action: str) -> str:
        headers = {
            "Content-Type": "text/xml; charset=utf-8",
            "SOAPAction": f"urn:schemas-microsoft-com:xml-analysis:{soap_action}",
        }
        resp = requests.post(self.url, headers=headers, data=soap_body.encode("utf-8"), auth=self.auth)
        resp.raise_for_status()
        return resp.text

    # --------------------------- discover ------------------------------

    def discover_dimensions(self, cube_name: str, format_type: str = "Tabular",
                            extra_properties: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """Список измерений куба."""
        body = self.DISCOVER_TEMPLATE.render(
            request_type=escape("MDSCHEMA_DIMENSIONS"),
            restrictions={"CUBE_NAME": escape(cube_name)},
            catalog=escape(self.catalog),
            datasource=escape(self.datasource),
            format_type=escape(format_type),
            extra_properties=extra_properties or {},
        )
        return self._parse_rows(self._send(body, "Discover"))

    def discover_dimension_members(self, cube_name: str, dimension: str, hierarchy: Optional[str] = None,
                                   level: str = "LEVEL01", format_type: str = "Tabular",
                                   extra_properties: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """Члены уровня измерения через MDSCHEMA_MEMBERS."""
        hierarchy = hierarchy or dimension
        dim_unique = self._bracket_if_needed(dimension)
        hier_unique = self._bracket_if_needed(hierarchy)
        lvl_unique = f"{hier_unique}.[{level}]"
        restrictions = {
            "CATALOG_NAME": escape(self.catalog),
            "CUBE_NAME": escape(cube_name),
            "DIMENSION_UNIQUE_NAME": escape(dim_unique),
            "HIERARCHY_UNIQUE_NAME": escape(hier_unique),
            "LEVEL_UNIQUE_NAME": escape(lvl_unique),
        }
        body = self.DISCOVER_TEMPLATE.render(
            request_type=escape("MDSCHEMA_MEMBERS"),
            restrictions=restrictions,
            format_type=escape(format_type),
            datasource=escape(self.datasource),
            extra_properties=extra_properties or {},
        )
        return self._parse_rows(self._send(body, "Discover"))

    def discover_levels(self, cube_name: str, format_type: str = "Tabular",
                        extra_properties: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """Список уровней и иерархий."""
        body = self.DISCOVER_TEMPLATE.render(
            request_type=escape("MDSCHEMA_LEVELS"),
            restrictions={"CUBE_NAME": escape(cube_name)},
            catalog=escape(self.catalog),
            datasource=escape(self.datasource),
            format_type=escape(format_type),
            extra_properties=extra_properties or {},
        )
        return self._parse_rows(self._send(body, "Discover"))

    def discover_all_dimension_unique_names(self, cube_name: str, format_type: str = "Tabular",
                                            extra_properties: Optional[Dict[str, Any]] = None) -> List[str]:
        """Все DIMENSION_UNIQUE_NAME через MDSCHEMA_HIERARCHIES."""
        body = self.DISCOVER_TEMPLATE.render(
            request_type=escape("MDSCHEMA_HIERARCHIES"),
            restrictions={"CATALOG_NAME": escape(self.catalog), "CUBE_NAME": escape(cube_name)},
            catalog=escape(self.catalog),
            datasource=escape(self.datasource),
            format_type=escape(format_type),
            extra_properties=extra_properties or {},
        )
        df = self._parse_rows(self._send(body, "Discover"))
        return sorted(
            df['DIMENSION_UNIQUE_NAME'].dropna().unique().tolist()) if 'DIMENSION_UNIQUE_NAME' in df.columns else []

    def discover_member_properties(self, cube_name: str, dimension: str, hierarchy: Optional[str] = None,
                                   extra_properties: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """Список PROPERTY_NAME для измерения/иерархии через MDSCHEMA_PROPERTIES."""
        hierarchy = hierarchy or dimension
        dim_unique = self._bracket_if_needed(dimension)
        hier_unique = self._bracket_if_needed(hierarchy)
        restrictions = {
            "CATALOG_NAME": escape(self.catalog),
            "CUBE_NAME": escape(cube_name),
            "DIMENSION_UNIQUE_NAME": escape(dim_unique),
            "HIERARCHY_UNIQUE_NAME": escape(hier_unique),
        }
        body = self.DISCOVER_TEMPLATE.render(
            request_type=escape("MDSCHEMA_PROPERTIES"),
            restrictions=restrictions,
            catalog=escape(self.catalog),
            datasource=escape(self.datasource),
            format_type=escape("Tabular"),
            extra_properties=extra_properties or {},
        )
        return self._parse_rows(self._send(body, "Discover"))

    # --------------------------- execute --------------------------------

    def execute_mdx(self, mdx: str) -> pd.DataFrame:
        """
        Выполнить MDX. Счётчик времени сохранён без изменений.
        """
        stop_counter = threading.Event()

        def display_timer():
            print("DEBUG: Счетчик запущен")
            start_time = time.time()
            while not stop_counter.is_set():
                elapsed_time = time.time() - start_time
                print(f"\rВремя выполнения: {elapsed_time:.2f} секунд", end='', flush=True)
                time.sleep(0.1)
            print("\rDEBUG: Счетчик остановлен")

        print("DEBUG: Запуск потока счетчика")
        timer_thread = threading.Thread(target=display_timer)
        timer_thread.daemon = True
        timer_thread.start()

        print("DEBUG: Начало выполнения запроса")
        start_query_time = time.time()
        body = f"""
            <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                              xmlns:x="urn:schemas-microsoft-com:xml-analysis">
              <soapenv:Header/>
              <soapenv:Body>
                <x:Execute>
                  <x:Command>
                    <x:Statement>{mdx}</x:Statement>
                  </x:Command>
                  <x:Properties>
                    <x:PropertyList>
                      <x:Catalog>{self.catalog}</x:Catalog>
                      <x:DataSourceInfo>{self.datasource}</x:DataSourceInfo>
                      <x:Format>Tabular</x:Format>
                      <x:AxisFormat>TupleFormat</x:AxisFormat>
                    </x:PropertyList>
                  </x:Properties>
                </x:Execute>
              </soapenv:Body>
            </soapenv:Envelope>
        """
        xml = self._send(body, "Execute")
        print("DEBUG: Запрос завершен")

        stop_counter.set()
        timer_thread.join()

        final_time = time.time() - start_query_time
        print(f"\r{' ' * 50}", end='', flush=True)
        print(f"\rЗапрос завершен за {final_time:.2f} секунд")
        return self._parse_rows(xml)

    # ------------------------ convenience API ---------------------------

    def get_members_with_attributes(self, cube_name: str, dimension: str, hierarchy: Optional[str] = None,
                                    attributes: Optional[List[str]] = None,
                                    extra_properties: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Один ИО + его атрибуты. Поведение сохранено как в твоём коде:
        если attributes не заданы — autoload через MDSCHEMA_PROPERTIES.
        """
        hierarchy = hierarchy or dimension
        dim_u = self._bracket_if_needed(dimension)

        if not attributes:
            df_props = self.discover_member_properties(cube_name, dimension, hierarchy,
                                                       extra_properties=extra_properties)
            if df_props.empty or "PROPERTY_NAME" not in df_props.columns:
                raise ValueError("Discover MDSCHEMA_PROPERTIES пустой или нет колонки PROPERTY_NAME")
            attributes = df_props["PROPERTY_NAME"].dropna().unique().tolist()

        props_clause = self._build_props_clause([(dim_u, attributes)])
        mdx = self._build_single_dim_mdx(cube_name, dim_u, "LEVEL01", props_clause)
        return self.execute_mdx(mdx)

    def get_members_with_attributes_multi(self, cube_name: str, dims: Sequence[Union[str, Dict[str, Any]]],
                                          extra_properties: Optional[Dict[str, Any]] = None,
                                          batch_size: Optional[int] = None,
                                          batch_on: int = 0,
                                          autoload: bool = False) -> pd.DataFrame:
        """
        Несколько ИО (CrossJoin) + атрибуты. По умолчанию свойства НЕ автоподтягиваются.
        """
        if not dims:
            return pd.DataFrame()

        specs = self._normalize_dims(dims)
        dim_attrs: List[Tuple[str, Optional[List[str]]]] = []

        for s in specs:
            attrs = s.attributes
            if autoload and not attrs:
                df_props = self.discover_member_properties(cube_name, s.dimension, s.hierarchy,
                                                           extra_properties=extra_properties)
                if df_props.empty or "PROPERTY_NAME" not in df_props.columns:
                    raise ValueError("Discover MDSCHEMA_PROPERTIES пустой или нет колонки PROPERTY_NAME")
                attrs = df_props["PROPERTY_NAME"].dropna().unique().tolist()
            dim_attrs.append((s.dim_unique, attrs))

        props_clause = self._build_props_clause(dim_attrs)
        level_sets = [self._level_members(s.dim_unique, s.level) for s in specs]

        # один запрос
        if not batch_size or batch_size <= 0:
            rows = self._cross_join(level_sets)
            mdx = self._build_rows_mdx(cube_name, rows, props_clause)
            return self.execute_mdx(mdx)

        # батчевка
        if batch_on < 0 or batch_on >= len(specs):
            raise IndexError(f"batch_on={batch_on} вне диапазона (0..{len(specs) - 1})")

        pivot = specs[batch_on]
        df_members = self.discover_dimension_members(cube_name, pivot.dimension, pivot.hierarchy, pivot.level)
        if df_members.empty or "MEMBER_UNIQUE_NAME" not in df_members.columns:
            raise RuntimeError(f"Не удалось получить членов для батчевки по измерению {pivot.dimension}")

        member_names = df_members["MEMBER_UNIQUE_NAME"].dropna().tolist()
        other = [ls for i, ls in enumerate(level_sets) if i != batch_on]
        other_rows = self._cross_join(other) if other else None

        parts: List[pd.DataFrame] = []
        for i in range(0, len(member_names), batch_size):
            chunk = member_names[i:i + batch_size]
            members_set = "{ " + ", ".join(chunk) + " }"
            rows = f"CrossJoin({members_set}, {other_rows})" if other_rows else members_set
            mdx = self._build_rows_mdx(cube_name, rows, props_clause)
            df_part = self.execute_mdx(mdx)
            if not df_part.empty:
                parts.append(df_part)
        return pd.concat(parts, ignore_index=True) if parts else pd.DataFrame()

    def validate_mdx_dimensions(self, mdx_query: str, cube_name: str) -> Dict[str, Any]:
        """Сравнить измерения, использованные в MDX, со всеми доступными в кубе."""

        def extract_dimensions_from_mdx(mdx: str) -> set:
            matches = re.findall(r'\[([^\[\]]+?)\]', mdx)
            ignore = {'Measures'}
            return {m.split('.')[0] for m in matches if m.split('.')[0] not in ignore}

        used = extract_dimensions_from_mdx(mdx_query)
        df = self.discover_dimensions(cube_name)
        available = set(df["DIMENSION_NAME"])
        return {
            "used": used,
            "available": available,
            "matched": used & available,
            "missing": used - available,
        }

    # ----------------------------- internals ----------------------------

    @staticmethod
    def _bracket_if_needed(name: str) -> str:
        return name if name.startswith('[') else f'[{name}]'

    @staticmethod
    def _level_members(dim_unique: str, level: str) -> str:
        # важно: оставляем твой стиль: без [] вокруг LEVEL01
        return f"{dim_unique}.{level}.Members"

    @staticmethod
    def _cross_join(level_sets: Sequence[str]) -> str:
        it = iter(level_sets)
        rows = next(it)
        for s in it:
            rows = f"CrossJoin({rows}, {s})"
        return rows

    @staticmethod
    def _build_props_clause(dim_attrs: Sequence[Tuple[str, Optional[List[str]]]]) -> str:
        """
        Собирает DIMENSION PROPERTIES в твоём формате:
          MEMBER_UNIQUE_NAME, MEMBER_CAPTION, [DIM].ATTR, ...
        """
        # props: List[str] = ["MEMBER_UNIQUE_NAME", "MEMBER_CAPTION"]
        props: List[str] = []
        for dim_u, attrs in dim_attrs:
            if attrs:
                for a in attrs:
                    props.append(f"{dim_u}.{a}")
        return ", ".join(props)

    @staticmethod
    def _build_single_dim_mdx(cube_name: str, dim_unique: str, level: str, props_clause: str) -> str:
        return f"""
            SELECT
              NON EMPTY {{}} ON COLUMNS,
              NON EMPTY {dim_unique}.{level}.Members
                DIMENSION PROPERTIES {props_clause}
              ON ROWS
            FROM [{cube_name}]
        """

    @staticmethod
    def _build_rows_mdx(cube_name: str, rows_set: str, props_clause: str) -> str:
        return f"""
            SELECT
              NON EMPTY {{}} ON COLUMNS,
              NON EMPTY {rows_set}
                DIMENSION PROPERTIES {props_clause}
              ON ROWS
            FROM [{cube_name}]
        """

    @staticmethod
    def _parse_rows(xml_text: str) -> pd.DataFrame:
        """Парсинг табличного ответа XMLA (rowset)."""
        try:
            root = ET.fromstring(xml_text)
            rows = root.findall('.//x:row', {'x': 'urn:schemas-microsoft-com:xml-analysis:rowset'})
            data = [{cell.tag.split('}')[-1]: cell.text for cell in row} for row in rows]
            return pd.DataFrame(data) if data else pd.DataFrame()
        except ET.ParseError as e:
            raise ValueError(f"Failed to parse XML response: {str(e)}")

    def _normalize_dims(self, dims: Sequence[Union[str, Dict[str, Any]]]) -> List[_DimSpec]:
        """
        Приводит входной список dims к унифицированному виду (_DimSpec),
        сохраняя твои дефолты: hierarchy=dimension, level='LEVEL01'.
        """
        out: List[_DimSpec] = []
        for d in dims:
            if isinstance(d, str):
                dim = d
                hier = d
                lvl = "LEVEL01"
                attrs: Optional[List[str]] = None
            elif isinstance(d, dict):
                dim = d.get("dimension")
                hier = d.get("hierarchy") or dim
                lvl = d.get("level", "LEVEL01")
                attrs = d.get("attributes")
            else:
                raise ValueError(f"Unsupported dim spec: {d!r}")
            dim_u = self._bracket_if_needed(dim)
            out.append(_DimSpec(dimension=dim, hierarchy=hier, level=lvl, attributes=attrs, dim_unique=dim_u))
        return out


# ----------------------------- пример запуска -----------------------------
if __name__ == '__main__':
    config_path = Path.home() / ".sap_bw.yml"
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    bwclient = SAPXMLAClient(url=config['SAP_URL'],
                             username=config['SAP_USER'],
                             password=config['SAP_PASS'])

    # примеры
    # df1 = bwclient.get_members_with_attributes("$HA01D003", "ZHA_VHVIN")
    df2 = bwclient.get_members_with_attributes_multi(
        "$HA01D003",
        dims=[
            {"dimension": "ZHA_VHVIN", "attributes": ["[2ZHA_VHVIN]", "[2ZHPTSNO]"]
             },
            {
                "dimension": "0CUSTOMER",
                "attributes": ["[20CUSTOMER]", "[50CUSTOMER]"]
                # "attributes": []
            },
            # {"dimension": "0COMP_CODE", "attributes": ["0COMP_CODE__TXT"]},
        ],
        autoload=False
    )
