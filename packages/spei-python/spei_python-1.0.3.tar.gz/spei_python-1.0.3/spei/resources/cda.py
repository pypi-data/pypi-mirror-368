from typing import Optional

from lxml import etree
from pydantic import BaseModel, ConfigDict

from spei import types
from spei.resources.validators import normalize_invalid_chars
from spei.utils import to_pascal_case, to_snake_case  # noqa: WPS347

SOAP_NS = 'http://schemas.xmlsoap.org/soap/envelope/'
PRAXIS_NS = 'http://www.praxis.com.mx/'
ENVIO_PRAXIS_NS = 'http://www.praxis.com.mx/EnvioCda/'


class CDA(BaseModel):
    model_config = ConfigDict(strict=False, coerce_numbers_to_str=True)

    id: int
    mensaje_id: int
    op_fecha_oper: DateInt
    op_fecha_abono: DateInt
    op_hora_abono: int

    op_cve_rastreo: str

    op_folio_orig_odp: int
    op_folio_orig_paq: int

    op_clave_emisor: InstitutionCode
    op_nombre_emisor: str

    op_tipo_pag: types.TipoPagoOrdenPago

    op_monto: str

    op_nombre_receptor: str

    op_concepto_pag: Optional[str] = None
    op_concepto_pag_2: Optional[str] = None

    op_nom_ord: Optional[str] = None
    op_tp_cta_ord: Optional[types.TipoCuentaOrdenPago] = None
    op_cuenta_ord: Optional[str] = None
    op_rfc_curp_ord: Optional[str] = None

    op_nom_ben: Optional[str] = None
    op_tp_cta_ben: Optional[types.TipoCuentaOrdenPago] = None
    op_cuenta_ben: Optional[str] = None
    op_rfc_curp_ben: Optional[str] = None

    op_iva: Optional[str] = None
    op_hora_00: Optional[int] = None

    op_nom_part_indirecto_ord: Optional[str] = None
    op_cta_part_indirecto_ord: Optional[str] = None
    op_rfc_curp_part_indirecto_ord: Optional[str] = None

    # remesas
    op_id_remesa: Optional[str] = None
    op_pais: Optional[str] = None
    op_divisa: Optional[str] = None
    op_nom_emisor_rem: Optional[str] = None
    op_cta_emisor_rem: Optional[str] = None
    op_rfc_curp_emisor_rem: Optional[str] = None
    op_nom_ben_rem: Optional[str] = None
    op_cta_ben_rem: Optional[str] = None
    op_rfc_curp_ben_rem: Optional[str] = None
    op_nom_prov_rem_ext: Optional[str] = None
    op_nom_prov_rem_nac: Optional[str] = None
    model_config = ConfigDict(use_enum_values=True)

    @classmethod
    def parse_xml(cls, mensaje_element):
        genera_cda = mensaje_element.find('generaCda')
        datos_cta = genera_cda.find('datosCda')

        cda_data = {
            'id': datos_cta.attrib['idCda'],
            'mensaje_id': datos_cta.attrib['idMensaje'],
        }

        for element in datos_cta.getchildren():
            tag = to_snake_case(element.tag)
            if tag in cls.model_fields:
                cda_data[tag] = element.text

        return cls(**cda_data)

    def build_xml(self) -> etree._Element:  # noqa: WPS437
        mensaje = etree.Element(
            etree.QName(ENVIO_PRAXIS_NS, 'datosCda'),
            idCda=str(self.id),
            idMensaje=str(self.mensaje_id),
            nsmap={'env': ENVIO_PRAXIS_NS},
        )

        elements = self.dict(exclude_none=True, exclude={'id', 'mensaje_id'})

        for element, value in elements.items():  # noqa: WPS110
            if element in self.__fields__:
                pascal_case_element = to_pascal_case(element)
                subelement = etree.SubElement(
                    mensaje,
                    etree.QName(ENVIO_PRAXIS_NS, pascal_case_element),
                )
                subelement.text = normalize_invalid_chars(value)

        return mensaje
