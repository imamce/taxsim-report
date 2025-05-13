import streamlit as st
import matplotlib.pyplot as plt
from PIL import Image
import os

# 한글 폰트 설정
plt.rcParams['font.family'] = 'Malgun Gothic'

def calc_simple_tax(income):
    if income <= 12000000:
        return income * 0.06
    elif income <= 46000000:
        return income * 0.15 - 1080000
    elif income <= 88000000:
        return income * 0.24 - 5220000
    elif income <= 150000000:
        return income * 0.35 - 14900000
    elif income <= 300000000:
        return income * 0.38 - 19400000
    elif income <= 500000000:
        return income * 0.4 - 25400000
    elif income <= 1000000000:
        return income * 0.42 - 35400000
    else:
        return income * 0.45 - 65400000

def calculate_fee(income):
    if income < 100_000_000:
        return 300_000
    elif income < 300_000_000:
        return 300_000 + (income - 100_000_000) * 2 / 1000
    elif income < 500_000_000:
        return 700_000 + (income - 300_000_000) * 2 / 1000
    elif income < 1_000_000_000:
        return 1_100_000 + (income - 500_000_000) * 1 / 1000
    elif income < 1_500_000_000:
        return 1_600_000 + (income - 1_000_000_000) * 1 / 1000
    elif income < 2_000_000_000:
        return 2_100_000 + (income - 1_500_000_000) * 1 / 1000
    elif income < 3_000_000_000:
        return 2_600_000 + (income - 2_000_000_000) * 1 / 1000
    elif income < 5_000_000_000:
        return 3_600_000 + (income - 3_000_000_000) * 1 / 1000
    elif income < 10_000_000_000:
        return 5_600_000 + (income - 5_000_000_000) * 1 / 1000
    else:
        return 0

def main():
    st.set_page_config(page_title="편한세무회계 종합소득세 리포트", layout="centered")

    st.sidebar.title("입력 데이터")
    name = st.sidebar.text_input("성함 입력", value="OOO")

    if 'biz_list' not in st.session_state:
        st.session_state.biz_list = [{"id": 1, "name": "사업장 1"}]
        st.session_state.next_id = 2

    def add_biz():
        st.session_state.biz_list.append({
            "id": st.session_state.next_id,
            "name": f"사업장 {st.session_state.next_id}"
        })
        st.session_state.next_id += 1

    def delete_biz(biz_id):
        st.session_state.biz_list = [b for b in st.session_state.biz_list if b["id"] != biz_id]

    business_data = []
    for biz in st.session_state.biz_list:
        with st.sidebar.expander(f"{biz['name']}"):
            biz_name = st.text_input("사업장 이름", value=biz["name"], key=f"bizname_{biz['id']}")
            income = st.number_input("수입금액", min_value=0, key=f"income_{biz['id']}")
            actual_profit = st.number_input("(가경비 반영전) 실제 손익", min_value=0, key=f"actual_{biz['id']}")
            book_profit = st.number_input("(가경비 반영후) 장부상 손익", min_value=0, key=f"book_{biz['id']}")
            st.button("삭제", key=f"delete_{biz['id']}", on_click=delete_biz, args=(biz['id'],))
            business_data.append({
                "이름": biz_name,
                "수입금액": income,
                "실제손익": actual_profit,
                "장부손익": book_profit
            })

    st.sidebar.button("사업장 추가", on_click=add_biz)
    tax_paid = st.sidebar.number_input("납부하실 세금", key="tax_paid")  # 음수 허용
    input_sum_of_others = st.sidebar.number_input("합계 (㉘+㉙+㉚)", min_value=0, key="manual_total")
    fee_surcharge = st.sidebar.number_input("수수료 할증(감면)", value=0, step=1000)
    extra_deduction_name = st.sidebar.text_input("추가 감면사항명")
    extra_deduction_amount = st.sidebar.number_input("추가 감면사항 금액", min_value=0, value=0, step=1000)

    total_income = sum(b["수입금액"] for b in business_data)
    total_actual_profit = sum(b["실제손익"] for b in business_data)
    total_book_profit = sum(b["장부손익"] for b in business_data)

    estimated_tax = calc_simple_tax(total_actual_profit)
    tax_saved = max(estimated_tax - input_sum_of_others, 0)
    auto_fee = calculate_fee(total_income)
    final_fee = auto_fee + fee_surcharge

    # ✅ 상대경로로 로고 불러오기 (Streamlit Cloud용)
    if os.path.exists("logo.jpg"):
        img = Image.open("logo.jpg")
        st.image(img, use_container_width=False, width=200)

    st.write(f"## {name}님 2024년 종합소득세 보고서")

    st.markdown(
        f"""
        <script>
        document.title = "[편한세무회계] {name}님 2024년 종합소득세 보고서";
        </script>
        """,
        unsafe_allow_html=True
    )

    st.write("---")
    st.write("### 요약 정보")
    col1, col2, col3, col4 = st.columns(4)
    col1.markdown(f"**수입금액**<br>{int(total_income):,}원", unsafe_allow_html=True)
    col2.markdown(f"**납부하실 세금**<br>{int(tax_paid):,}원", unsafe_allow_html=True)
    col3.markdown(f"**절세 성공액**<br>{int(tax_saved):,}원", unsafe_allow_html=True)
    col4.markdown(f"**조정료(VAT 별도)**<br>{int(final_fee):,}원", unsafe_allow_html=True)

    st.write("---")
    st.write("### 2024년 종합소득세 요약")
    st.write(f"**반영 소득(사업장)** : {len(business_data)}개")
    for b in business_data:
        st.write(f"- {b['이름']} 수입금액: {int(b['수입금액']):,}원 / 장부상 손익: {int(b['장부손익']):,}원")
    st.write(f"- 장부상 손익 합계: {int(total_book_profit):,}원")
    st.write(f"- 단순 세율 적용 예상세액(A): {int(estimated_tax):,}원")
    st.write(f"- 실제 산출세액(B): {int(input_sum_of_others):,}원")
    st.write(f"- 절세 성공액 = A - B → {int(tax_saved):,}원")

    if extra_deduction_name or extra_deduction_amount > 0:
        st.write(f"**추가 감면사항**: {extra_deduction_name} ( {extra_deduction_amount:,}원 )")

    st.markdown(
        """
        <div style='font-size:0.95em; color:#1f77b4; margin-top:10px;'>
        ※본 보고서는 편한세무회계 고객님만을 위해 제공된 자료입니다. 허가되지 않은 외부 배포를 금합니다.
        </div>
        """,
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
