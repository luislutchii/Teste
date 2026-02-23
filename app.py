import streamlit as st
import requests
import time

# ===============================
# CONFIG
# ===============================

API_URL = "https://api-cs.casino.org/svc-evolution-game-events/api/lightningbacbo/latest"

PADROES = [
    (["🔵","🔴"], "🔵"),
    (["🔴","🔵"], "🔴"),
    (["🔵","🔵"], "🔴"),
    (["🔴","🔴"], "🔵"),
    (["🔵","🔴","🔵"], "🔴"),
    (["🔴","🔵","🔴"], "🔵"),
    (["🔵","🔵","🔵"], "🔴"),
    (["🔴","🔴","🔴"], "🔵"),
]

# ===============================
# SESSION STATE
# ===============================

if "history" not in st.session_state:
    st.session_state.history = []

if "wins" not in st.session_state:
    st.session_state.wins = 0

if "losses" not in st.session_state:
    st.session_state.losses = 0

if "signal" not in st.session_state:
    st.session_state.signal = None

if "last_round" not in st.session_state:
    st.session_state.last_round = None


# ===============================
# FUNÇÕES
# ===============================

def buscar_resultado():
    try:
        r = requests.get(API_URL, timeout=5)
        data = r.json()

        game = data.get("data", data)

        round_id = game.get("id") or game.get("roundId")
        outcome_raw = game.get("result", {}).get("outcome")

        if not round_id or not outcome_raw:
            return None, None

        if "Player" in outcome_raw:
            outcome = "🔵"
        elif "Banker" in outcome_raw:
            outcome = "🔴"
        elif "Tie" in outcome_raw:
            outcome = "🟡"
        else:
            return None, None

        return round_id, outcome

    except:
        return None, None


def gerar_sinal():
    history = st.session_state.history
    for seq, sinal in PADROES:
        if history[-len(seq):] == seq:
            return sinal
    return None


def calcular_assertividade():
    total = st.session_state.wins + st.session_state.losses
    if total == 0:
        return 0
    return round((st.session_state.wins / total) * 100, 2)


# ===============================
# INTERFACE
# ===============================

st.set_page_config(page_title="Bac Bo AI", layout="centered")

st.title("🔥 BAC BO AI SINAIS")

placeholder = st.empty()

while True:

    round_id, outcome = buscar_resultado()

    if round_id and round_id != st.session_state.last_round:

        st.session_state.last_round = round_id
        st.session_state.history.append(outcome)
        st.session_state.history = st.session_state.history[-20:]

        # Verificar resultado do sinal anterior
        if st.session_state.signal:

            if outcome == "🟡":
                st.session_state.wins += 1
            elif outcome == st.session_state.signal:
                st.session_state.wins += 1
            else:
                st.session_state.losses += 1

            st.session_state.signal = None

        # Gerar novo sinal
        novo_sinal = gerar_sinal()
        if novo_sinal:
            st.session_state.signal = novo_sinal

    with placeholder.container():

        st.subheader("Histórico")
        st.write(" ".join(st.session_state.history[-10:]))

        st.subheader("Sinal Atual")
        if st.session_state.signal:
            st.markdown(f"# {st.session_state.signal}")
        else:
            st.write("Aguardando padrão...")

        st.subheader("Estatísticas")
        col1, col2, col3 = st.columns(3)

        col1.metric("Green", st.session_state.wins)
        col2.metric("Loss", st.session_state.losses)
        col3.metric("Assertividade", f"{calcular_assertividade()}%")

    time.sleep(5)
    st.rerun()