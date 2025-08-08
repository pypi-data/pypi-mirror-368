import json
import logging
import re
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import pdfplumber

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


@dataclass
class RegistryProperty:
    """표제부 - 건물 기본 정보"""

    register_number: Optional[str] = None
    received_date: Optional[str] = None
    building_number: Optional[str] = None
    structure: Optional[str] = None
    area: Optional[float] = None  # 면적을 float 타입으로 변경
    usage: Optional[str] = None
    registration_cause: Optional[str] = None
    location: Optional[str] = None


@dataclass
class LandRight:
    """대지권 정보"""

    display_number: Optional[str] = None
    land_right_type: Optional[str] = None
    land_right_ratio: Optional[str] = None
    registration_details: Optional[str] = None
    land_right_total_area: Optional[float] = None  # 분모 (전체 면적)
    land_right_area: Optional[float] = None  # 분자 (해당 면적)


@dataclass
class OwnershipRecord:
    """갑구 - 소유권 정보"""

    order_number: Optional[str] = None
    registration_purpose: Optional[str] = None
    received_date: Optional[str] = None
    registration_cause: Optional[str] = None
    owner_info: Optional[str] = None
    share_ratio: Optional[str] = None


@dataclass
class RightRecord:
    """을구 - 소유권 이외 권리"""

    order_number: Optional[str] = None
    registration_purpose: Optional[str] = None
    received_date: Optional[str] = None
    registration_cause: Optional[str] = None
    right_holder: Optional[str] = None
    right_details: Optional[str] = None
    mortgage_amount: Optional[str] = None


@dataclass
class RegistryDocument:
    """등기부등본 전체 구조"""

    document_info: Dict[str, Any]
    property_info: RegistryProperty
    land_rights: List[LandRight]
    ownership_records: List[OwnershipRecord]
    right_records: List[RightRecord]
    raw_sections: Dict[str, Any]
    validation_results: Dict[str, Any]


class RegistryParser:
    """향상된 등기부등본 종합 파서 v2.2"""

    def __init__(self):
        self.logger = logger
        self.section_patterns = {
            "표제부": r"【\s*표\s*제\s*부\s*】",
            "갑구": r"【\s*갑\s*구\s*】",
            "을구": r"【\s*을\s*구\s*】",
            "대지권": r"대지권의?\s*표시",
        }

        # 개선된 컬럼 매핑 사전
        self.column_mappings = {
            "표제부": {
                "register_number": ["표시번호", "번호"],
                "received_date": ["접수", "접수일", "접수일자"],
                "building_number": ["건물번호", "건물명칭", "번호"],
                "structure": ["구조", "건물구조"],
                "area": ["면적", "전유부분"],
                "location": ["소재지", "소재", "위치"],
            },
            "갑구": {
                "order_number": ["순위번호", "순위", "번호"],
                "registration_purpose": ["등기목적", "목적"],
                "received_date": ["접수", "접수일", "접수일자"],
                "registration_cause": ["등기원인", "원인"],
                "owner_info": ["소유자", "권리자", "성명"],
                "share_ratio": ["지분", "비율", "지분비율"],
            },
            "을구": {
                "order_number": ["순위번호", "순위", "번호"],
                "registration_purpose": ["등기목적", "목적"],
                "received_date": ["접수", "접수일", "접수일자"],
                "registration_cause": ["등기원인", "원인"],
                "right_holder": ["권리자", "성명", "채권자"],
                "right_details": ["권리내용", "내용"],
                "mortgage_amount": ["채권최고액", "금액", "최고액"],
            },
        }

    def parse_pdf(self, pdf_path: str) -> RegistryDocument:
        """PDF 등기부등본을 파싱합니다"""
        self.logger.info(f"향상된 등기부등본 파싱 시작: {pdf_path}")
        self._log("PDF 파싱 시작")

        try:
            # PDF 읽기
            with pdfplumber.open(pdf_path) as pdf:
                full_text = ""
                tables_data = []

                for page_num, page in enumerate(pdf.pages, 1):
                    self._log(f"페이지 {page_num} 처리 중")

                    # 텍스트 추출
                    page_text = page.extract_text()
                    if page_text:
                        full_text += f"\n--- 페이지 {page_num} ---\n{page_text}"
                        self._debug_log(
                            f"페이지 {page_num} 텍스트 길이: {len(page_text)}"
                        )

                    # 테이블 추출 (여러 설정으로 시도)
                    tables = page.extract_tables()
                    if not tables:
                        # 다른 설정으로 테이블 추출 시도
                        tables = page.extract_tables(
                            table_settings={
                                "vertical_strategy": "lines",
                                "horizontal_strategy": "lines",
                            }
                        )

                    if tables:
                        for i, table in enumerate(tables):
                            tables_data.append(
                                {"page": page_num, "table_index": i, "data": table}
                            )
                        self._log(f"페이지 {page_num}에서 {len(tables)}개 테이블 발견")
                        self._debug_log(
                            f"페이지 {page_num} 첫 번째 테이블 크기: {len(tables[0]) if tables else 0}x{len(tables[0][0]) if tables and tables[0] else 0}"
                        )

            # 전체 텍스트 샘플 로그
            self._debug_log(f"전체 텍스트 첫 500자: {full_text[:500]}...")

            # 섹션 분리 (개선된 버전)
            sections = self._identify_sections_v3(full_text, tables_data)
            self._log(f"식별된 섹션: {list(sections.keys())}")

            # 각 섹션 상세 정보 로그
            for section_name, section_data in sections.items():
                self._debug_log(
                    f"{section_name} 섹션 텍스트 길이: {len(section_data.get('text', ''))}"
                )
                self._debug_log(
                    f"{section_name} 섹션 테이블 수: {len(section_data.get('tables', []))}"
                )
                if section_data.get("text"):
                    self._debug_log(
                        f"{section_name} 섹션 텍스트 샘플: {section_data['text'][:200]}..."
                    )

            # 각 섹션 파싱 (개선된 버전)
            property_info = self._parse_property_section_v3(sections.get("표제부", {}))
            land_rights = self._parse_land_rights_section_v3(sections.get("대지권", {}))
            ownership_records = self._parse_ownership_section_v3(
                sections.get("갑구", {})
            )
            right_records = self._parse_rights_section_v3(sections.get("을구", {}))

            # 검증 수행
            validation_results = self._validate_parsed_data_v3(
                property_info, land_rights, ownership_records, right_records
            )

            # 결과 구성
            document = RegistryDocument(
                document_info={
                    "source_file": pdf_path,
                    "parsed_at": datetime.now().isoformat(),
                    "total_pages": len(pdf.pages) if "pdf" in locals() else 0,
                    "total_tables": len(tables_data),
                    "parser_version": "2.2",
                },
                property_info=property_info,
                land_rights=land_rights,
                ownership_records=ownership_records,
                right_records=right_records,
                raw_sections=sections,
                validation_results=validation_results,
            )

            self.logger.info("등기부등본 파싱 완료")
            return document

        except Exception as e:
            self.logger.error(f"파싱 중 오류 발생: {str(e)}")
            self._log(f"오류: {str(e)}")
            raise

    def _identify_sections_v3(
        self, full_text: str, tables_data: List[Dict]
    ) -> Dict[str, Dict]:
        """등기부등본의 섹션들을 식별합니다 (v3 - 완전 개선)"""
        sections = {}
        lines = full_text.split("\n")

        current_section = None
        section_start_line = 0

        # 섹션 패턴을 순서대로 찾기
        for line_num, line in enumerate(lines):
            line_clean = line.strip()

            # 섹션 시작 감지 (개선된 패턴)
            section_found = None

            # 표제부 패턴
            if re.search(r"【\s*표\s*제\s*부\s*】", line_clean):
                # 1동의 건물과 전유부분을 구분
                if "1동의 건물" in line_clean:
                    section_found = "표제부_1동"
                elif "전유부분" in line_clean:
                    section_found = "표제부"
                else:
                    section_found = "표제부"
            # 갑구 패턴
            elif re.search(r"【\s*갑\s*구\s*】", line_clean):
                section_found = "갑구"
            # 을구 패턴
            elif re.search(r"【\s*을\s*구\s*】", line_clean):
                section_found = "을구"
            # 대지권 패턴
            elif re.search(r"대지권의?\s*표시", line_clean):
                section_found = "대지권"

            if section_found:
                # 이전 섹션 완료
                if current_section:
                    section_text = "\n".join(lines[section_start_line:line_num])
                    sections[current_section] = {
                        "text": section_text,
                        "start_line": section_start_line,
                        "end_line": line_num - 1,
                    }
                    self._debug_log(
                        f"섹션 '{current_section}' 완료: {len(section_text)} 문자"
                    )

                # 새 섹션 시작
                current_section = section_found
                section_start_line = line_num
                self._log(f"섹션 '{section_found}' 시작 (라인 {line_num})")

        # 마지막 섹션 처리
        if current_section:
            section_text = "\n".join(lines[section_start_line:])
            sections[current_section] = {
                "text": section_text,
                "start_line": section_start_line,
                "end_line": len(lines) - 1,
            }
            self._debug_log(
                f"마지막 섹션 '{current_section}' 완료: {len(section_text)} 문자"
            )

        # 대지권 섹션 별도 검색 (【 패턴이 없을 수도 있음)
        if "대지권" not in sections:
            self._search_land_rights_section_v3(lines, sections)

        # 테이블 데이터를 적절한 섹션에 할당 (개선된 버전)
        self._assign_tables_to_sections_v3(sections, tables_data, full_text)

        return sections

    def _search_land_rights_section_v3(self, lines: List[str], sections: Dict):
        """대지권 섹션을 별도로 검색합니다 (v3)"""
        land_rights_patterns = [
            r"대지권의?\s*표시",
            r"대지권\s*종류",
            r"대지권\s*비율",
            r"소유권대지권",
            r"\d+분의\s*[\d.]+",  # 대지권 비율 패턴
        ]

        for line_num, line in enumerate(lines):
            line_clean = line.strip()
            for pattern in land_rights_patterns:
                if re.search(pattern, line_clean):
                    # 대지권 섹션 발견
                    start_line = max(0, line_num - 2)
                    end_line = min(len(lines), line_num + 10)
                    section_text = "\n".join(lines[start_line:end_line])

                    sections["대지권"] = {
                        "text": section_text,
                        "start_line": start_line,
                        "end_line": end_line - 1,
                    }
                    self._log(f"대지권 섹션 발견 (라인 {line_num})")
                    self._debug_log(f"대지권 섹션 텍스트: {section_text[:200]}...")
                    return

    def _assign_tables_to_sections_v3(
        self, sections: Dict, tables_data: List[Dict], full_text: str
    ):
        """테이블을 적절한 섹션에 할당합니다 (v3 - 완전 개선)"""

        # 각 섹션별로 테이블 할당 초기화
        for section_name in sections.keys():
            sections[section_name]["tables"] = []

        for table_info in tables_data:
            table = table_info["data"]
            if not table or len(table) == 0:
                continue

            # 테이블 내용을 문자열로 변환
            table_text = " ".join(
                [" ".join(str(cell) for cell in row if cell) for row in table if row]
            ).lower()

            # 테이블 첫 행 분석
            first_row = table[0] if table else []
            first_row_text = " ".join(str(cell) for cell in first_row if cell).lower()

            assigned = False
            best_match = None
            best_score = 0

            # 각 섹션과의 매칭 점수 계산
            for section_name in sections.keys():
                score = self._calculate_table_section_score_v3(
                    section_name, table_text, first_row_text, table
                )

                self._debug_log(
                    f"테이블 (페이지 {table_info['page']}) - {section_name} 매칭 점수: {score}"
                )

                if score > best_score:
                    best_score = score
                    best_match = section_name

            # 임계값 이상이면 할당
            if best_match and best_score >= 3:
                sections[best_match]["tables"].append(table_info)
                self._log(
                    f"테이블이 '{best_match}' 섹션에 할당됨 (페이지 {table_info['page']}, 점수: {best_score})"
                )
                self._debug_log(
                    f"할당된 테이블 첫 행: {first_row[:3] if first_row else '없음'}"
                )
                assigned = True

            if not assigned:
                self._debug_log(
                    f"테이블 (페이지 {table_info['page']}) 할당 실패 - 최고 점수: {best_score}"
                )

    def _calculate_table_section_score_v3(
        self, section_name: str, table_text: str, first_row_text: str, table: List[List]
    ) -> int:
        """테이블과 섹션 간의 매칭 점수를 계산합니다 (v3)"""

        # 섹션별 키워드 정의 (개선)
        keywords = {
            "표제부": [
                "표시번호",
                "접수",
                "건물번호",
                "구조",
                "면적",
                "전유부분",
                "소재지",
                "건물내역",
            ],
            "표제부_1동": [
                "표시번호",
                "접수",
                "소재지번",
                "건물명칭",
                "건물내역",
                "1동의건물",
            ],
            "갑구": [
                "순위번호",
                "등기목적",
                "소유자",
                "지분",
                "소유권",
                "소유권이전",
                "소유권보존",
            ],
            "을구": [
                "순위번호",
                "등기목적",
                "권리자",
                "채권최고액",
                "근저당권",
                "전세권",
                "소유권이외",
            ],
            "대지권": ["대지권종류", "대지권비율", "표시번호", "소유권대지권"],
        }

        # 특별 패턴 (강력한 식별자)
        special_patterns = {
            "표제부": [r"【\s*표\s*제\s*부\s*】", r"전유부분"],
            "표제부_1동": [r"1동의\s*건물", r"【\s*표\s*제\s*부\s*】"],
            "갑구": [
                r"【\s*갑\s*구\s*】",
                r"소유권에\s*관한",
                r"소유자\s+\w+",
                r"소유권이전",
            ],
            "을구": [
                r"【\s*을\s*구\s*】",
                r"소유권\s*이외",
                r"근저당권",
                r"채권최고액",
            ],
            "대지권": [r"대지권의?\s*표시", r"소유권대지권", r"\d+분의\s*[\d.]+"],
        }

        section_keywords = keywords.get(section_name, [])
        section_patterns = special_patterns.get(section_name, [])

        score = 0

        # 1. 특별 패턴 매칭 (높은 가중치)
        for pattern in section_patterns:
            if re.search(pattern, table_text):
                score += 5
            if re.search(pattern, first_row_text):
                score += 8

        # 2. 키워드 매칭
        keyword_score = sum(1 for keyword in section_keywords if keyword in table_text)
        header_score = sum(
            1 for keyword in section_keywords if keyword in first_row_text
        )

        score += keyword_score + header_score * 2

        # 3. 갑구/을구 구분 강화
        if section_name == "갑구":
            if "소유자" in table_text and "소유권" in table_text:
                score += 10
            if "채권최고액" in table_text or "근저당권" in table_text:
                score -= 5  # 을구 특징이면 감점

        elif section_name == "을구":
            if "채권최고액" in table_text or "근저당권" in table_text:
                score += 10
            if (
                re.search(r"소유자\s+\w+", table_text)
                and "채권최고액" not in table_text
            ):
                score -= 5  # 갑구 특징이면 감점

        return score

    def _parse_property_section_v3(self, section_data: Dict) -> RegistryProperty:
        """표제부 섹션을 파싱합니다 (v3 - 완전 개선)"""
        if not section_data:
            return RegistryProperty()

        self._log("표제부 섹션 파싱 시작")
        property_info = RegistryProperty()

        text = section_data.get("text", "")
        tables = section_data.get("tables", [])

        # 개선된 정규표현식 패턴
        patterns = {
            "register_number": r"(?:표시번호\s*[:：]?\s*)?(\d+)\s*(?:\(전\s*\d+\))?",
            "received_date": r"(\d{4}년\d{1,2}월\d{1,2}일)",
            "building_number": r"제\s*(\d+층\s*제\d+호)",
            "structure": r"(철근콘크리트조[^\n]*)",
            "area": r"(\d+\.?\d*㎡)",
            "location": r"서울특별시[^\n]+",
        }

        # 텍스트에서 정보 추출
        for field, pattern in patterns.items():
            matches = re.findall(pattern, text, re.MULTILINE)
            if matches:
                # 가장 적절한 매치 선택
                value = self._select_best_match(field, matches)
                if value and len(value) < 100:
                    # 면적 필드는 float로 변환
                    if field == "area":
                        area_float = self._parse_area_to_float(value)
                        if area_float is not None:
                            setattr(property_info, field, area_float)
                            self._log(
                                f"표제부에서 {field} 추출: {value} → {area_float}"
                            )
                    else:
                        setattr(property_info, field, value)
                        self._log(f"표제부에서 {field} 추출: {value}")

        # 테이블에서 상세 정보 추출 (개선)
        if tables:
            for table_info in tables:
                table = table_info["data"]
                property_info = self._extract_property_from_table_v3(
                    property_info, table
                )

        return property_info

    def _select_best_match(self, field: str, matches: List[str]) -> str:
        """필드별로 가장 적절한 매치를 선택합니다"""
        if not matches:
            return ""

        if field == "register_number":
            # 가장 작은 숫자 (일반적으로 1)
            return min(
                matches,
                key=lambda x: int(re.findall(r"\d+", x)[0])
                if re.findall(r"\d+", x)
                else 999,
            )
        elif field == "building_number":
            # 층과 호수가 있는 것
            return next((m for m in matches if "층" in m and "호" in m), matches[0])
        elif field == "area":
            # 가장 작은 면적 (전유부분) - 면적 1000㎡ 미만인 것 우선
            valid_areas = []
            for match in matches:
                numeric_match = re.findall(r"[\d.]+", match)
                if numeric_match:
                    try:
                        area_value = float(numeric_match[0])
                        if area_value < 1000:  # 전유부분은 보통 작음
                            valid_areas.append((match, area_value))
                    except ValueError:
                        continue

            if valid_areas:
                return min(valid_areas, key=lambda x: x[1])[0]
            else:
                return matches[0] if matches else ""
        else:
            return matches[0]

    def _extract_property_from_table_v3(
        self, property_info: RegistryProperty, table: List[List[str]]
    ) -> RegistryProperty:
        """테이블에서 표제부 정보를 추출합니다 (v3)"""
        if not table:
            return property_info

        self._debug_log(
            f"표제부 테이블 크기: {len(table)}x{len(table[0]) if table else 0}"
        )

        # 건물번호, 구조, 면적 등 직접 추출
        for row in table:
            if not row:
                continue

            row_text = " ".join(str(cell) for cell in row if cell)

            # 건물번호 (제5층 제506호 형태)
            if not property_info.building_number:
                building_match = re.search(r"제\s*(\d+층\s*제\d+호)", row_text)
                if building_match:
                    property_info.building_number = building_match.group(1)
                    self._log(
                        f"표제부 테이블에서 building_number 추출: {building_match.group(1)}"
                    )

            # 구조 (철근콘크리트조)
            if not property_info.structure:
                structure_match = re.search(r"(철근콘크리트조)", row_text)
                if structure_match:
                    property_info.structure = structure_match.group(1)
                    self._log(
                        f"표제부 테이블에서 structure 추출: {structure_match.group(1)}"
                    )

            # 면적 (59.69㎡ 형태)
            if not property_info.area:
                area_match = re.search(r"(\d+\.?\d*㎡)", row_text)
                if area_match:
                    area_text = area_match.group(1)
                    area_float = self._parse_area_to_float(area_text)
                    # 전유부분은 보통 작음 (1000㎡ 미만)
                    if area_float is not None and area_float < 1000:
                        property_info.area = area_float
                        self._log(
                            f"표제부 테이블에서 area 추출: {area_text} → {area_float}"
                        )

        return property_info

    def _parse_land_rights_section_v3(self, section_data: Dict) -> List[LandRight]:
        """대지권 섹션을 파싱합니다 (v3)"""
        if not section_data:
            return []

        self._log("대지권 섹션 파싱 시작")
        land_rights = []

        text = section_data.get("text", "")
        tables = section_data.get("tables", [])

        # 텍스트에서 대지권 정보 직접 추출
        land_rights_from_text = self._extract_land_rights_from_text_v3(text)
        land_rights.extend(land_rights_from_text)

        # 테이블에서 대지권 정보 추출
        if tables:
            for table_info in tables:
                table = table_info["data"]
                if not table:
                    continue

                land_rights_from_table = self._extract_land_rights_from_table_v3(table)
                land_rights.extend(land_rights_from_table)

        # 중복 제거
        unique_land_rights = []
        seen = set()
        for lr in land_rights:
            key = (lr.display_number, lr.land_right_type, lr.land_right_ratio)
            if key not in seen:
                seen.add(key)
                unique_land_rights.append(lr)

        self._log(f"대지권에서 {len(unique_land_rights)}개 레코드 추출됨")
        return unique_land_rights

    def _extract_land_rights_from_text_v3(self, text: str) -> List[LandRight]:
        """텍스트에서 직접 대지권 정보를 추출합니다 (v3)"""
        land_rights = []

        # 대지권 패턴 매칭
        land_right_pattern = (
            r"(\d+)\s+(\d+\s*소유권대지권)\s+(\d+분의\s*[\d.]+)\s+(.*?)(?=\n|$)"
        )
        matches = re.findall(land_right_pattern, text, re.MULTILINE)

        for match in matches:
            display_number, land_right_type, land_right_ratio, registration_details = (
                match
            )

            # 대지권 비율에서 면적 정보 파싱
            total_area, area = self._parse_land_right_fraction(land_right_ratio.strip())

            land_right = LandRight(
                display_number=display_number.strip(),
                land_right_type=land_right_type.strip(),
                land_right_ratio=land_right_ratio.strip(),
                registration_details=registration_details.strip()
                if registration_details.strip()
                else None,
                land_right_total_area=total_area,
                land_right_area=area,
            )

            land_rights.append(land_right)
            self._log(
                f"텍스트에서 대지권 추출: {land_right.display_number} - {land_right.land_right_type} (전체: {total_area}, 면적: {area})"
            )

        return land_rights

    def _extract_land_rights_from_table_v3(
        self, table: List[List[str]]
    ) -> List[LandRight]:
        """테이블에서 대지권 정보를 추출합니다 (v3)"""
        land_rights = []

        # 대지권 테이블 헤더 찾기
        header_row = None
        for i, row in enumerate(table):
            if row and any("대지권종류" in str(cell) for cell in row if cell):
                header_row = i
                break

        if header_row is None:
            return land_rights

        headers = table[header_row]

        # 컬럼 인덱스 매핑
        col_mapping = {}
        for j, header in enumerate(headers):
            header_str = str(header) if header else ""
            if "표시번호" in header_str:
                col_mapping["display_number"] = j
            elif "대지권종류" in header_str:
                col_mapping["land_right_type"] = j
            elif "대지권비율" in header_str:
                col_mapping["land_right_ratio"] = j
            elif "등기원인" in header_str:
                col_mapping["registration_details"] = j

        # 데이터 행 처리
        for i in range(header_row + 1, len(table)):
            row = table[i]
            if not row or not any(str(cell).strip() for cell in row if cell):
                continue

            land_right = LandRight()

            # 각 컬럼 데이터 추출
            for field, col_idx in col_mapping.items():
                if col_idx < len(row) and row[col_idx]:
                    value = str(row[col_idx]).strip()
                    if value:
                        setattr(land_right, field, value)

            # 대지권 비율에서 면적 정보 파싱
            if land_right.land_right_ratio:
                total_area, area = self._parse_land_right_fraction(
                    land_right.land_right_ratio
                )
                land_right.land_right_total_area = total_area
                land_right.land_right_area = area

            # 유효한 대지권만 추가
            if land_right.land_right_type or land_right.land_right_ratio:
                land_rights.append(land_right)

        return land_rights

    def _parse_ownership_section_v3(self, section_data: Dict) -> List[OwnershipRecord]:
        """갑구(소유권) 섹션을 파싱합니다 (v3 - 완전 개선)"""
        if not section_data:
            return []

        self._log("갑구 섹션 파싱 시작")
        ownership_records = []

        text = section_data.get("text", "")
        tables = section_data.get("tables", [])

        # 텍스트에서 직접 소유자 정보 추출
        ownership_from_text = self._extract_ownership_from_text_v3(text)
        ownership_records.extend(ownership_from_text)

        # 테이블에서 소유권 정보 추출
        if tables:
            for table_info in tables:
                table = table_info["data"]
                if not table:
                    continue

                # 갑구 테이블인지 확인
                if self._is_ownership_table_v3(table):
                    ownership_from_table = self._extract_ownership_from_table_v3(table)
                    ownership_records.extend(ownership_from_table)

        self._log(f"갑구에서 {len(ownership_records)}개 레코드 추출됨")
        return ownership_records

    def _extract_ownership_from_text_v3(self, text: str) -> List[OwnershipRecord]:
        """텍스트에서 소유권 정보를 추출합니다 (v3)"""
        ownership_records = []

        # 소유권 패턴 매칭
        ownership_patterns = [
            r"(\d+)\s+(소유권\w*)\s+(\d{4}년\d{1,2}월\d{1,2}일[^\n]*)\s+([^\n]*)\s+(소유자[^\n]+)",
            r"소유자\s+(\w+)\s+(\d{6}-\*+)\s+([^\n]+)",
        ]

        for pattern in ownership_patterns:
            matches = re.findall(pattern, text, re.MULTILINE)
            for match in matches:
                if len(match) == 5:  # 완전한 소유권 레코드
                    (
                        order_number,
                        registration_purpose,
                        received_date,
                        registration_cause,
                        owner_info,
                    ) = match

                    record = OwnershipRecord(
                        order_number=order_number.strip(),
                        registration_purpose=registration_purpose.strip(),
                        received_date=received_date.strip(),
                        registration_cause=registration_cause.strip(),
                        owner_info=owner_info.strip(),
                    )

                    ownership_records.append(record)
                    owner_preview = (
                        record.owner_info[:30] if record.owner_info else "정보없음"
                    )
                    self._log(
                        f"텍스트에서 소유권 추출: {record.order_number} - {owner_preview}..."
                    )

                elif len(match) == 3:  # 소유자 정보만
                    name, ssn, address = match
                    record = OwnershipRecord(
                        owner_info=f"소유자 {name} {ssn} {address}"
                    )
                    ownership_records.append(record)

        return ownership_records

    def _is_ownership_table_v3(self, table: List[List]) -> bool:
        """테이블이 갑구(소유권) 테이블인지 판단합니다 (v3)"""
        table_text = " ".join(
            [" ".join(str(cell) for cell in row if cell) for row in table if row]
        ).lower()

        # 갑구 특징
        ownership_indicators = [
            "소유자",
            "소유권이전",
            "소유권보존",
            "갑구",
            "소유권에관한",
        ]
        # 을구 특징 (배제)
        rights_indicators = ["채권최고액", "근저당권", "전세권", "을구"]

        ownership_score = sum(
            1 for indicator in ownership_indicators if indicator in table_text
        )
        rights_score = sum(
            1 for indicator in rights_indicators if indicator in table_text
        )

        return ownership_score > rights_score and ownership_score >= 2

    def _extract_ownership_from_table_v3(
        self, table: List[List]
    ) -> List[OwnershipRecord]:
        """테이블에서 소유권 정보를 추출합니다 (v3)"""
        ownership_records = []

        # 헤더 찾기
        header_row = None
        for i, row in enumerate(table):
            if row and any("순위번호" in str(cell) for cell in row if cell):
                header_row = i
                break

        if header_row is None:
            return ownership_records

        headers = table[header_row]

        # 컬럼 매핑
        col_mapping = {}
        for j, header in enumerate(headers):
            header_str = str(header).lower() if header else ""
            if "순위번호" in header_str or "순위" in header_str:
                col_mapping["order_number"] = j
            elif "등기목적" in header_str or "목적" in header_str:
                col_mapping["registration_purpose"] = j
            elif "접수" in header_str:
                col_mapping["received_date"] = j
            elif "등기원인" in header_str or "원인" in header_str:
                col_mapping["registration_cause"] = j
            elif "권리자" in header_str or "기타사항" in header_str:
                col_mapping["owner_info"] = j

        # 데이터 행 처리
        for i in range(header_row + 1, len(table)):
            row = table[i]
            if not row or not any(str(cell).strip() for cell in row if cell):
                continue

            record = OwnershipRecord()

            # 소유자 정보가 있는지 확인
            has_owner_info = False
            for cell in row:
                if cell and "소유자" in str(cell):
                    has_owner_info = True
                    break

            if not has_owner_info:
                continue

            # 각 컬럼 데이터 추출
            for field, col_idx in col_mapping.items():
                if col_idx < len(row) and row[col_idx]:
                    value = str(row[col_idx]).strip()
                    if value:
                        setattr(record, field, value)

            if record.owner_info or record.registration_purpose:
                ownership_records.append(record)

        return ownership_records

    def _parse_rights_section_v3(self, section_data: Dict) -> List[RightRecord]:
        """을구(권리) 섹션을 파싱합니다 (v3)"""
        if not section_data:
            return []

        self._log("을구 섹션 파싱 시작")
        return self._parse_tabular_section_v3(section_data, "을구", RightRecord)

    def _parse_tabular_section_v3(
        self, section_data: Dict, section_type: str, record_class
    ) -> List:
        """테이블 형태의 섹션(을구)을 파싱합니다 (v3)"""
        records = []
        tables = section_data.get("tables", [])

        if not tables:
            self._log(f"{section_type} 섹션에 테이블이 없습니다")
            return records

        for table_idx, table_info in enumerate(tables):
            table = table_info["data"]
            if not table:
                continue

            # 을구 테이블인지 확인 (갑구와 구분)
            if section_type == "을구" and not self._is_rights_table_v3(table):
                self._debug_log(
                    f"{section_type} 테이블 {table_idx} - 갑구 테이블로 판단, 스킵"
                )
                continue

            self._debug_log(
                f"{section_type} 테이블 {table_idx} 크기: {len(table)}x{len(table[0]) if table else 0}"
            )

            # 헤더 찾기
            header_row = self._find_header_row_v3(table, section_type)
            if header_row is None:
                self._debug_log(
                    f"{section_type} 테이블 {table_idx}에서 헤더를 찾을 수 없음"
                )
                continue

            headers = table[header_row]
            col_mapping = self._map_columns_v3(headers, section_type)

            self._debug_log(f"{section_type} 테이블 {table_idx} 헤더: {headers}")
            self._log(f"{section_type} 컬럼 매핑: {col_mapping}")

            # 데이터 행 처리
            table_records = self._extract_records_from_table_v3(
                table, header_row, col_mapping, record_class, section_type
            )
            records.extend(table_records)

        self._log(f"{section_type}에서 {len(records)}개 레코드 추출됨")
        return records

    def _is_rights_table_v3(self, table: List[List]) -> bool:
        """테이블이 을구(권리) 테이블인지 판단합니다 (v3)"""
        table_text = " ".join(
            [" ".join(str(cell) for cell in row if cell) for row in table if row]
        ).lower()

        # 을구 특징
        rights_indicators = ["채권최고액", "근저당권", "전세권", "을구", "소유권이외"]
        # 갑구 특징 (배제)
        ownership_indicators = ["소유자", "소유권이전", "소유권보존"]

        rights_score = sum(
            1 for indicator in rights_indicators if indicator in table_text
        )
        ownership_score = sum(
            1 for indicator in ownership_indicators if indicator in table_text
        )

        # 갑구 특징이 강하면 제외
        if (
            ownership_score > 0
            and "소유자" in table_text
            and "채권최고액" not in table_text
        ):
            return False

        return rights_score > ownership_score or rights_score >= 1

    def _find_header_row_v3(
        self, table: List[List], section_type: str
    ) -> Optional[int]:
        """헤더 행을 찾습니다 (v3)"""
        keywords = {
            "갑구": ["순위번호", "등기목적", "소유자", "접수"],
            "을구": ["순위번호", "등기목적", "권리자", "채권최고액", "접수"],
        }

        section_keywords = keywords.get(section_type, [])

        best_row = -1
        best_score = 0

        for i, row in enumerate(table):
            if not row:
                continue

            row_text = " ".join(str(cell) for cell in row if cell).lower()

            # 키워드 매칭 점수 계산
            score = sum(1 for keyword in section_keywords if keyword in row_text)

            if score > best_score:
                best_score = score
                best_row = i

        # 최소 2개 키워드는 매칭되어야 함
        if best_score >= 2:
            self._debug_log(f"{section_type} 헤더 행 {best_row} (점수: {best_score})")
            return best_row

        return None

    def _map_columns_v3(self, headers: List, section_type: str) -> Dict[str, int]:
        """헤더를 분석하여 컬럼 매핑을 생성합니다 (v3)"""
        col_mapping = {}
        mappings = self.column_mappings.get(section_type, {})

        for field, keywords in mappings.items():
            best_col = -1
            best_score = 0

            for i, header in enumerate(headers):
                if not header:
                    continue

                header_str = str(header).strip().lower()

                # 키워드 매칭 점수 계산
                score = sum(1 for keyword in keywords if keyword in header_str)

                if score > best_score:
                    best_score = score
                    best_col = i

            if best_score > 0:
                col_mapping[field] = best_col

        return col_mapping

    def _extract_records_from_table_v3(
        self,
        table: List[List],
        header_row: int,
        col_mapping: Dict[str, int],
        record_class,
        section_type: str,
    ) -> List:
        """테이블에서 레코드들을 추출합니다 (v3)"""
        records = []
        current_record = None

        for i in range(header_row + 1, len(table)):
            row = table[i]
            if not row:
                continue

            # 을구에서는 소유자 정보가 있는 행 제외
            if section_type == "을구":
                row_text = " ".join(str(cell) for cell in row if cell)
                if (
                    "소유자" in row_text
                    and "채권최고액" not in row_text
                    and "근저당권" not in row_text
                ):
                    self._debug_log(f"을구에서 갑구 데이터 스킵: {row_text[:50]}...")
                    continue

            # 순위번호가 있으면 새로운 레코드 시작
            order_col = col_mapping.get("order_number")
            is_new_record = False

            if order_col is not None and order_col < len(row) and row[order_col]:
                order_value = str(row[order_col]).strip()
                # 순위번호 패턴 확인
                if order_value and (
                    order_value.isdigit() or re.match(r"\d+[-\s]?\d*", order_value)
                ):
                    is_new_record = True
                    self._debug_log(
                        f"{section_type} 새로운 레코드 시작: 순위 {order_value}"
                    )

            if is_new_record and current_record:
                records.append(current_record)

            if is_new_record or current_record is None:
                current_record = record_class()

            # 현재 행 데이터를 레코드에 추가
            self._extract_row_data_v3(current_record, row, col_mapping)

        # 마지막 레코드 저장
        if current_record:
            records.append(current_record)

        return records

    def _extract_row_data_v3(self, record, row: List, col_mapping: Dict[str, int]):
        """행 데이터를 레코드 객체에 추출합니다 (v3)"""
        for field, col_idx in col_mapping.items():
            if col_idx < len(row) and row[col_idx]:
                value = str(row[col_idx]).strip()
                if value:
                    # 기존 값이 있으면 추가
                    current_value = getattr(record, field, None)
                    if current_value:
                        if len(current_value) < 500:
                            setattr(record, field, f"{current_value}\n{value}")
                    else:
                        setattr(record, field, value)

    def _validate_parsed_data_v3(
        self, property_info, land_rights, ownership_records, right_records
    ) -> Dict[str, Any]:
        """파싱된 데이터를 검증합니다 (v3)"""
        validation = {
            "is_valid": True,
            "warnings": [],
            "errors": [],
            "statistics": {
                "property_fields_filled": 0,
                "land_rights_count": len(land_rights),
                "ownership_records_count": len(ownership_records),
                "right_records_count": len(right_records),
            },
        }

        # 표제부 검증
        property_fields = asdict(property_info)
        filled_fields = sum(1 for v in property_fields.values() if v)
        validation["statistics"]["property_fields_filled"] = filled_fields

        if filled_fields == 0:
            validation["errors"].append("표제부 정보가 전혀 추출되지 않았습니다")
            validation["is_valid"] = False
        elif filled_fields < 3:
            validation["warnings"].append("표제부 정보가 부족합니다")

        # 갑구 검증
        if len(ownership_records) == 0:
            validation["warnings"].append("갑구(소유권) 정보가 추출되지 않았습니다")

        # 대지권 검증
        if len(land_rights) == 0:
            validation["warnings"].append("대지권 정보가 추출되지 않았습니다")

        return validation

    def _log(self, message: str):
        """파싱 로그 기록"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"{timestamp} - {message}"
        self.logger.info(log_message)

    def _debug_log(self, message: str):
        """디버그 로그 기록"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_message = f"{timestamp} - DEBUG - {message}"
        self.logger.info(log_message)

    def _parse_land_right_fraction(
        self, fraction_text: str
    ) -> tuple[Optional[float], Optional[float]]:
        """대지권 비율 분수를 파싱합니다 (예: '10939분의 24.111' → (10939.0, 24.111))"""
        if not fraction_text:
            return None, None

        # '분의' 패턴으로 분수 추출
        fraction_pattern = r"(\d+(?:\.\d+)?)분의\s*(\d+(?:\.\d+)?)"
        match = re.search(fraction_pattern, fraction_text)

        if match:
            try:
                total_area = float(match.group(1))
                area = float(match.group(2))
                self._debug_log(
                    f"분수 파싱 성공: {fraction_text} → 전체: {total_area}, 면적: {area}"
                )
                return total_area, area
            except ValueError as e:
                self._debug_log(f"분수 파싱 실패 (숫자 변환): {fraction_text} - {e}")
                return None, None
        else:
            self._debug_log(f"분수 패턴 매칭 실패: {fraction_text}")
            return None, None

    def _parse_area_to_float(self, area_text: str) -> Optional[float]:
        """면적 텍스트에서 특수문자를 제거하고 float로 변환합니다 (예: '59.69㎡' → 59.69)"""
        if not area_text:
            return None

        # 숫자와 소수점만 추출
        numeric_pattern = r"(\d+(?:\.\d+)?)"
        match = re.search(numeric_pattern, area_text)

        if match:
            try:
                area_value = float(match.group(1))
                self._debug_log(f"면적 파싱 성공: {area_text} → {area_value}")
                return area_value
            except ValueError as e:
                self._debug_log(f"면적 파싱 실패 (숫자 변환): {area_text} - {e}")
                return None
        else:
            self._debug_log(f"면적 패턴 매칭 실패: {area_text}")
            return None

    def to_json(
        self, document: RegistryDocument, include_raw: bool = False
    ) -> Dict[str, Any]:
        """등기부등본 문서를 JSON으로 변환합니다"""
        result = {
            "document_info": document.document_info,
            "property_info": asdict(document.property_info),
            "land_rights": [asdict(lr) for lr in document.land_rights],
            "ownership_records": [asdict(or_) for or_ in document.ownership_records],
            "right_records": [asdict(rr) for rr in document.right_records],
            "validation_results": document.validation_results,
        }

        if include_raw:
            result["raw_sections"] = document.raw_sections

        return result

    def save_results(self, document: RegistryDocument, base_filename: str):
        """JSON과 요약 리포트만 저장합니다"""
        # JSON 저장
        json_data = self.to_json(document, include_raw=True)
        json_file = f"{base_filename}.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)

        self.logger.info(
            f"결과 저장 완료: {base_filename}.json, {base_filename}_summary.txt"
        )


def test_multiple_pdfs():
    """여러 PDF 파일로 테스트"""
    pdf_dir = Path("/data/AI/dataset/pdf")
    parser = RegistryParser()

    pdf_files = list(pdf_dir.glob("*.pdf"))
    print(f"\n🧪 {len(pdf_files)}개 PDF 파일로 테스트 시작")

    results = []

    for pdf_file in pdf_files:
        print(f"\n{'=' * 60}")
        print(f"📄 테스트 중: {pdf_file.name}")
        print(f"{'=' * 60}")

        try:
            document = parser.parse_pdf(str(pdf_file))

            # 결과 저장 (JSON + 요약 리포트만)
            base_name = pdf_file.stem + "_parsed_v23"
            parser.save_results(document, str(pdf_dir / base_name))

            # 결과 요약
            val = document.validation_results
            stats = val["statistics"]

            result = {
                "file": pdf_file.name,
                "success": True,
                "property_fields": stats["property_fields_filled"],
                "land_rights": stats["land_rights_count"],
                "ownership_records": stats["ownership_records_count"],
                "right_records": stats["right_records_count"],
                "warnings": len(val["warnings"]),
                "errors": len(val["errors"]),
            }

            results.append(result)

            print(
                f"✅ 성공: 표제부 {stats['property_fields_filled']}/8, 대지권 {stats['land_rights_count']}, 갑구 {stats['ownership_records_count']}, 을구 {stats['right_records_count']}"
            )

        except Exception as e:
            print(f"❌ 실패: {str(e)}")
            results.append({"file": pdf_file.name, "success": False, "error": str(e)})

    # 전체 결과 요약
    print(f"\n{'=' * 60}")
    print("📊 전체 테스트 결과 요약")
    print(f"{'=' * 60}")

    successful = [r for r in results if r.get("success", False)]
    failed = [r for r in results if not r.get("success", False)]

    print(f"✅ 성공: {len(successful)}/{len(results)}")
    print(f"❌ 실패: {len(failed)}/{len(results)}")

    if successful:
        avg_property = sum(r["property_fields"] for r in successful) / len(successful)
        avg_land_rights = sum(r["land_rights"] for r in successful) / len(successful)
        avg_ownership = sum(r["ownership_records"] for r in successful) / len(
            successful
        )
        avg_rights = sum(r["right_records"] for r in successful) / len(successful)

        print("\n📈 평균 추출량:")
        print(f"  🏠 표제부: {avg_property:.1f}/8 필드")
        print(f"  🏡 대지권: {avg_land_rights:.1f}건")
        print(f"  👥 갑구: {avg_ownership:.1f}건")
        print(f"  ⚖️ 을구: {avg_rights:.1f}건")

    return results


def main():
    """메인 실행 함수"""
    print("📋 향상된 등기부등본 종합 파서 v2.3")
    print("=" * 60)

    # 사용법 안내
    print("🎯 이 도구는 PDF 등기부등본을 구조화된 JSON으로 변환합니다.")
    print("\n📁 지원 형식:")
    print("  • PDF → JSON (구조화된 데이터)")
    print("  • PDF → TXT (요약 리포트)")

    print("\n📋 옵션:")
    print("1. 단일 PDF 파일 파싱")
    print("2. 전체 PDF 파일 배치 테스트")

    choice = input("\n선택하세요 (1/2, 기본값: 1): ").strip()

    if choice == "2":
        test_multiple_pdfs()
    else:
        # 파일 선택
        pdf_file = input("\n📎 PDF 파일명을 입력하세요: ").strip()

        if not pdf_file:
            print("❌ 파일명이 입력되지 않았습니다.")
            return

        if not Path(pdf_file).exists():
            print(f"❌ 파일을 찾을 수 없습니다: {pdf_file}")
            return

        try:
            # 파서 초기화 및 실행
            parser = RegistryParser()
            document: RegistryDocument = parser.parse_pdf(pdf_file)

            # 결과 출력
            print("\n" + "=" * 60)
            print("📊 파싱 결과")
            print("=" * 60)

            # 검증 결과
            val = document.validation_results
            status = "✅ 성공" if val["is_valid"] else "❌ 실패"
            print(f"\n🔍 검증: {status}")
            if val["warnings"]:
                print(f"⚠️ 경고 {len(val['warnings'])}개")
                for warning in val["warnings"]:
                    print(f"  - {warning}")
            if val["errors"]:
                print(f"❌ 오류 {len(val['errors'])}개")
                for error in val["errors"]:
                    print(f"  - {error}")

            # 통계
            stats = val["statistics"]
            print("\n📊 추출 통계:")
            print(f"  🏠 표제부: {stats['property_fields_filled']}/8 필드")
            print(f"  🏡 대지권: {stats['land_rights_count']}건")
            print(f"  👥 갑구: {stats['ownership_records_count']}건")
            print(f"  ⚖️ 을구: {stats['right_records_count']}건")

            # 주요 정보 미리보기
            prop = document.property_info
            if prop.building_number:
                print(f"\n🏢 건물: {prop.building_number}")
            if prop.structure:
                print(f"🔨 구조: {prop.structure}")
            if prop.area:
                print(f"📐 면적: {prop.area}")

            # 파일 저장
            base_name = Path(pdf_file).stem + "_parsed_v23"
            parser.save_results(document, base_name)

            print("\n💾 결과 저장:")
            print(f"  📄 {base_name}.json")
            print(f"  📝 {base_name}_summary.txt")

        except Exception as e:
            print(f"❌ 오류 발생: {str(e)}")
            logger.error(f"메인 실행 오류: {str(e)}")


if __name__ == "__main__":
    main()
