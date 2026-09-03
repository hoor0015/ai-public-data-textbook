# -*- coding: utf-8 -*-
"""12주차 2회차: 전국 주민등록 총인구(2019-2023)의 연도별 증감을 다시 계산한다.

값은 6·12주차 실습에서 저자가 kosis MCP로 조회한 결과다
(통계표 "행정구역(시군구)별 성별 인구수", DT_1B040A3, 항목 총인구수, 전국, 단위 명).
실행: cd $HOME/default-uv-env && PYTHONIOENCODING=utf-8 VIRTUAL_ENV= uv run python "<이 파일 경로>"
"""
POP = {2019: 51_849_861, 2020: 51_829_023, 2021: 51_638_809,
       2022: 51_439_038, 2023: 51_325_329}

print("연도 | 총인구(명) | 전년 대비 증감(명)")
prev = None
for y in sorted(POP):
    diff = "" if prev is None else f"{POP[y] - POP[prev]:+,}"
    print(f"{y} | {POP[y]:,} | {diff}")
    prev = y

total = POP[2023] - POP[2019]
print(f"2019-2023 증감: {total:+,}명 ({total / POP[2019] * 100:+.2f}%)")
print(f"연평균 증감(4년 단순 평균): {total / 4:+,.0f}명/년 "
      f"({total / 4 / POP[2019] * 100:+.3f}%/년)")
