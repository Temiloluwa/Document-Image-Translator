from dataclasses import dataclass, asdict
import json


@dataclass
class OCRPageDimensions:
    dpi: int
    height: int
    width: int

    def json(self):
        return json.dumps(asdict(self))


@dataclass
class OCRPageObject:
    index: int
    markdown: str
    images: list
    dimensions: OCRPageDimensions

    def json(self):
        return json.dumps(asdict(self))


@dataclass
class OCRUsageInfo:
    pages_processed: int
    doc_size_bytes: int

    def json(self):
        return json.dumps(asdict(self))


@dataclass
class OCRResponse:
    pages: list
    model: str
    usage_info: OCRUsageInfo

    def json(self):
        return json.dumps(asdict(self))


mock_dimensions = OCRPageDimensions(dpi=200, height=1622, width=1164)
mock_page = OCRPageObject(
    index=0,
    markdown='# EUROZONE \n\n19 Lander, eine Währung: „Eurozone" ist die inoffizielle Bezeichnung für die 19 EU-Staaten, die Mitglied in der Europäischen Wirtschafts- und Währungsunion (WWU) sind und den Euro als gemeinsames Zahlungsmittel eingeführt haben. Die WWU startete 1999 mit elf Staaten, die übrigen\nkamen im Laufe der Jahre hinzu. Die Euro-Scheine und -münzen wurden im Jahr 2002 in Umlauf gebracht, damit wurden die nationalen Währungen als Zahlungsmittel abgelöst. Sitz der Europäischen Zentralbank (EZB) ist Frankfurt am Main. Präsidentin der EZB ist seit dem 1. November 2019 die Franzōsin\nChristine Lagarde.\n\n## Zahlen \\& Fakten\n\nDie EU ist eine in der Welt einmalige Konstruktion: Sie ist ein Zusammensehluss demokratischer europäischer Staaten, die sich die Wahrung des Friedens und das Streben nach Wohlstand als oberstes Ziel gesetzt haben.\n\n## NEUE MITGLIEDER\n\n$++$\n\nZwei Lander, die Chancen auf einen Beitritt zur EU haben, sind Albanien und Nordmazedonien.\n\nErst vor Kurzem haben die Mitgliedsländer dem Vorschlag der FU-Kommission zugestimmt.\n\nBeitrittsgesprache mit den beiden westlichen Balkanstaaten aufzunehmen. "ihre Zukunft liegt in der FU", sagt FU-Frweiterungskommissar Olivér Várnelyi. Die EU-Kommission macht sich seit Langem für eine Erweiterung auf dem westlichen Balkan stark\n\nEINWOHNER\n\n## DEUTLICHE UNTERSCHIEDE\n\nRund 447 Millionen Menschen leben in der 27 Mitgliedsländern der EU - nach Indien und China ist das die drittgröbte Bevolkerung der Welt. Mit 85,1 Millionen Einwohnern ist Deutschland der bevolkerungsreichste Mitgliedstaat, vor Frankreich ( 67 Millionen), Italien ( 60,4 Millionen), Spanien ( 46,9 Millionen) und Polen ( 57,9 Millionen). Mit dem Austritt Großbritannien Ende Januar 2020 verlor die EU rund 66,6 Millionen Einwohner. Die Fläche der Staatengemeinschaft beträgt mehr als vier Millionen km². Flächenmahig ist Frankreich das gröbte und Malta das kleinste Land der EU. Deutschland ist mit $557.576 \\mathrm{~km}^{2}$ der von der\nFlache her viertgröbte EU-Staat',
    images=[],
    dimensions=mock_dimensions,
)
mock_usage_info = OCRUsageInfo(pages_processed=1, doc_size_bytes=251937)

mock_ocr_response = OCRResponse(
    pages=[mock_page], model="mistral-ocr-2505-completion", usage_info=mock_usage_info
)
