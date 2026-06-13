import streamlit as st
from collections import deque

 
class DialogueNode:
    def __init__(self, node_id, bot_response, context):
        self.node_id = node_id
        self.bot_response = bot_response
        self.context = context
        self.children = []

    def add_child(self, child_node):
        self.children.append(child_node)

class DialogueTree:
    def __init__(self, root_node):
        self.root = root_node

    def bfs_search_context(self, target_context):
        if not self.root:
            return None
        queue = deque([self.root])
        visited = {self.root.node_id}
        while queue:
            current_node = queue.popleft()
            if current_node.context == target_context:
                return current_node
            for child in current_node.children:
                if child.node_id not in visited:
                    visited.add(child.node_id)
                    queue.append(child)
        return None

    def dfs_get_structure(self, node=None, depth=0, lines=None, visited=None):
        if lines is None:
            lines = []
        if visited is None:
            visited = set()   
            
        if node is None and depth == 0:
            node = self.root
            
         
        if node.node_id in visited:
            lines.append("  " * depth + f"• [{node.node_id}] Kontekst: '{node.context}' ↻ (Povratak/Ciklus)")
            return lines
            
         
        visited.add(node.node_id)
        
        lines.append("  " * depth + f"• [{node.node_id}] Kontekst: '{node.context}'")
        for child in node.children:
            self.dfs_get_structure(child, depth + 1, lines, visited)
            
        return lines
 
def inicijalizuj_stablo():
    root = DialogueNode("ROOT", "Zdravo! Ja sam Vaš AI asistent. Da li imate problem sa **internetom** ili Vas zanima **racun**?", "pocetak")
    
    internet = DialogueNode("INT_1", "Izabrali ste internet. Da li je problem sa **ruterom** ili je u pitanju **spora** veza?", "internet")
    racun = DialogueNode("RAC_1", "Izabrali ste račune. Da li Vas zanima trenutno **stanje** ili online **placanje**?", "racun")
    root.add_child(internet)
    root.add_child(racun)
    
    ruter = DialogueNode("INT_RUTER", "Molimo restartujte Vaš ruter na 10 sekundi. Da li lampica sada **svijetli** ili **ne_svijetli**?", "ruter")
    spora = DialogueNode("INT_SPORA", "Pokrenite Speedtest. Da li je brzina ispod ugovorene? (Odgovorite sa **da** ili **ne**)", "spora")
    internet.add_child(ruter)
    internet.add_child(spora)
    
    stanje = DialogueNode("RAC_STANJE", "Vaše trenutno stanje računa je 0.00 KM. Napišite 'pocetak' za povratak.", "stanje")
    placanje = DialogueNode("RAC_PLAY", "Online plaćanje možete izvršiti putem aplikacije. Napišite 'pocetak' za povratak.", "placanje")
    racun.add_child(stanje)
    racun.add_child(placanje)
    
    ruter_ok = DialogueNode("INT_R_OK", "Sjajno! Drago mi je da je problem uspješno riješen. Napišite 'pocetak' za novi chat.", "svijetli")
    ruter_fail = DialogueNode("INT_R_FAIL", "Problem nije riješen. Prosjeđujem Vas agentu tehničke podrške...", "ne_svijetli")
    ruter.add_child(ruter_ok)
    ruter.add_child(ruter_fail)
    
    stanje.add_child(root)
    placanje.add_child(root)
    ruter_ok.add_child(root)

    return DialogueTree(root)

def mock_gpt_intent_analyzer(user_input, current_node):
    input_lower = user_input.lower()
    for child in current_node.children:
        if child.context in input_lower:
            return child.context
    return None

 
st.set_page_config(page_title="AI Chatbot - Grafovi", page_icon="🤖", layout="wide")

st.title("🤖 GPT ChatBot sa Grafovskom Strukturom")
st.caption("Projekat iz Struktura Podataka i Algoritama - Vildan Ljuca")

 
if 'stablo' not in st.session_state:
    st.session_state.stablo = inicijalizuj_stablo()
    st.session_state.trenutni_cvor = st.session_state.stablo.root
    
    st.session_state.poruke = [{"role": "assistant", "content": st.session_state.trenutni_cvor.bot_response}]

 
kolona_chat, kolona_graf = st.columns([2, 1])

with kolona_chat:
    st.subheader("Razgovor sa Botom")
    
    
    for poruka in st.session_state.poruke:
        with st.chat_message(poruka["role"]):
            st.write(poruka["content"])

    
    if korisnik_unos := st.chat_input("Upišite Vaš odgovor ovdje..."):
       
        st.session_state.poruke.append({"role": "user", "content": korisnik_unos})
        
        
        sledeci_kontekst = mock_gpt_intent_analyzer(korisnik_unos, st.session_state.trenutni_cvor)
        
        if sledeci_kontekst:
            sledeci_cvor = st.session_state.stablo.bfs_search_context(sledeci_kontekst)
            if sledeci_cvor:
                st.session_state.trenutni_cvor = sledeci_cvor
                odgovor_bota = st.session_state.trenutni_cvor.bot_response
            else:
                odgovor_bota = "Greška u navigaciji kroz stablo."
        else:
            dostupne_opcije = [c.context for c in st.session_state.trenutni_cvor.children]
            odgovor_bota = f"Nisam Vas razumio. Trenutne opcije su: **{', '.join(dostupne_opcije)}**"
        
         
        st.session_state.poruke.append({"role": "assistant", "content": odgovor_bota})
        st.rerun()

with kolona_graf:
    st.subheader("Struktura grafa (DFS Mapa)")
    st.info("Ova kolona uživo simulira kako DFS algoritam vidi stablo dijaloga i označava gdje se trenutno nalaziš.")
    
     
    dfs_linije = st.session_state.stablo.dfs_get_structure()
    
    
    tekst_prikaza = ""
    for linija in dfs_linije:
        if f"[{st.session_state.trenutni_cvor.node_id}]" in linija:
            tekst_prikaza += f"**{linija} 🌟 (TRENUTNO STANJE)**\n\n"
        else:
            tekst_prikaza += f"{linija}\n\n"
            
    st.markdown(tekst_prikaza)