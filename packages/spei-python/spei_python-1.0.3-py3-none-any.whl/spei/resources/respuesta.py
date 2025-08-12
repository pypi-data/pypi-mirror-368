from typing import Optional, TypedDict

from lxml import etree
from pydantic import BaseModel, ConfigDict, Field

from spei import types
from spei.utils import to_pascal_case, to_snake_case  # noqa: WPS347


class DataDict(TypedDict, total=False):
    categoria: types.CategoriaOrdenPago
    id: Optional[str]
    fecha_oper: Optional[int]
    err_codigo: Optional[types.CodigoError]
    err_descripcion: Optional[str]


class Respuesta(BaseModel):
    model_config = ConfigDict(strict=False, coerce_numbers_to_str=True)

    categoria: types.CategoriaOrdenPago
    err_codigo: Optional[types.CodigoError] = Field(default=None, validate_default=True)
    id: Optional[int] = None
    fecha_oper: Optional[int] = None
    err_descripcion: Optional[str] = None
    model_config = ConfigDict(use_enum_values=True)

    def build_xml(self):
        respuesta = etree.Element('respuesta')

        for element, value in self.dict(exclude={'categoria'}).items():  # noqa: WPS110
            if element in self.__fields__:
                pascal_case_element = to_pascal_case(element)
                subelement = etree.SubElement(respuesta, pascal_case_element)
                subelement.text = str(value)

        return respuesta

    @classmethod
    def parse_xml(cls, respuesta_element, categoria: types.CategoriaOrdenPago):
        respuesta_data: DataDict = {
            'categoria': categoria,
        }

        for sub_element in respuesta_element.getchildren():
            tag = to_snake_case(sub_element.tag)
            respuesta_data[tag] = sub_element.text  # type: ignore

        return cls.model_validate(respuesta_data)
