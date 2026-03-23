#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔════════════════════════════════════════════════════════════════╗
║   🌹  مهووس — تطبيق المراجعة البصرية والإضافة               ║
║   Streamlit App — تطوير محرك v14                             ║
╚════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
import pandas as pd
import re, time, unicodedata, warnings, json, io, hashlib
from pathlib import Path
from collections import defaultdict
from rapidfuzz import fuzz, process as rfp
import requests

warnings.filterwarnings("ignore")

# ══════════════════════════════════════════════════════
#  PAGE CONFIG
# ══════════════════════════════════════════════════════
st.set_page_config(page_title="مهووس | محرك المنتجات", page_icon="🌹",
                   layout="wide", initial_sidebar_state="expanded")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Tajawal:wght@300;400;500;700;800;900&display=swap');
:root {
  --bg:#08080e; --surf:#111118; --card:#181820; --bord:#252535;
  --gold:#c9a84c; --gold2:#f0d070; --text:#e4e4f0; --muted:#6e6e88;
  --grn:#52c47d; --red:#e05050; --blue:#5c8ee0;
}
html,body,[class*="css"]{font-family:'Tajawal',sans-serif!important;direction:rtl;}
.stApp{background:var(--bg);color:var(--text);}
.main .block-container{padding:1.5rem 2rem;max-width:1900px;}
[data-testid="stSidebar"]{background:var(--surf)!important;border-left:1px solid var(--bord);}
.stTabs [data-baseweb="tab-list"]{background:var(--surf);border-radius:8px;gap:4px;padding:4px;}
.stTabs [data-baseweb="tab"]{color:var(--muted);padding:8px 18px;border-radius:6px;font-weight:600;}
.stTabs [aria-selected="true"]{color:var(--gold)!important;background:rgba(201,168,76,.12)!important;}
.brand-hdr{background:linear-gradient(90deg,rgba(201,168,76,.18),transparent);
  border-right:3px solid var(--gold);padding:.5rem 1rem;margin:1.5rem 0 .8rem;
  border-radius:0 8px 8px 0;font-size:1.05rem;font-weight:800;color:var(--gold2);}
.pcard{background:var(--card);border:1px solid var(--bord);border-radius:12px;
  padding:.9rem;margin-bottom:.7rem;transition:.2s;}
.pcard:hover{border-color:var(--gold);}
.pcard.approved{border-color:var(--grn)!important;background:rgba(82,196,125,.05);}
.pcard.rejected{opacity:.4;}
.badge{display:inline-block;padding:2px 9px;border-radius:20px;font-size:.72rem;font-weight:700;}
.badge-gold{background:linear-gradient(135deg,var(--gold),var(--gold2));color:#000;}
.badge-cnt{background:var(--bord);color:var(--gold);}
.badge-grn{background:rgba(82,196,125,.2);color:var(--grn);}
.badge-red{background:rgba(224,80,80,.2);color:var(--red);}
.pname{font-size:.88rem;font-weight:700;color:var(--text);line-height:1.4;margin:.4rem 0;}
.pprice{font-size:1.1rem;font-weight:900;color:var(--gold2);}
.pcomp{font-size:.72rem;color:var(--muted);}
.img-box{border-radius:8px;overflow:hidden;border:1px solid var(--bord);
  background:var(--surf);min-height:140px;display:flex;align-items:center;justify-content:center;}
.img-lbl{font-size:.65rem;color:var(--muted);text-align:center;margin-top:3px;}
.metric-card{background:var(--card);border:1px solid var(--bord);border-radius:10px;
  padding:1.1rem;text-align:center;}
.metric-val{font-size:2.2rem;font-weight:900;color:var(--gold);line-height:1;}
.metric-lbl{font-size:.75rem;color:var(--muted);margin-top:3px;}
.sec-title{font-size:1.4rem;font-weight:800;color:var(--gold2);
  border-bottom:1px solid var(--bord);padding-bottom:.5rem;margin-bottom:1rem;}
.desc-box{background:var(--surf);border:1px solid var(--bord);border-radius:8px;
  padding:1rem;font-size:.85rem;line-height:1.8;color:var(--text);
  max-height:400px;overflow-y:auto;}
.stButton>button{font-family:'Tajawal',sans-serif!important;}
div[data-testid="stNumberInput"]>div>input,
div[data-testid="stTextInput"]>div>input,
div[data-testid="stSelectbox"]>div{
  background:var(--card)!important;border-color:var(--bord)!important;color:var(--text)!important;}
textarea{background:var(--card)!important;color:var(--text)!important;
  border-color:var(--bord)!important;font-family:'Tajawal',sans-serif!important;}
.logo-title{text-align:center;padding:1rem 0 .5rem;}
.logo-t{font-size:2rem;font-weight:900;
  background:linear-gradient(135deg,var(--gold),var(--gold2));
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;}
.logo-s{font-size:.75rem;color:var(--muted);}
</style>""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════
#  V14 MATCHING ENGINE — CONSTANTS
# ══════════════════════════════════════════════════════
MIN_SIZE_ML = 16

CONC_PATTERNS = [
    (r"(?:اليكسير|ايسنس)\s+(?:دي|دو|دى)\s+(?:بارفيوم|برفيوم|بارفان|بيرفيوم)", "EDP"),
    (r"لو\s+(?:دي|دو|دى)\s+(?:بارفيوم|برفيوم|بارفان|بيرفيوم)", "EDP"),
    (r"(?:او|أو|اودي|اودو|اودى)\s+(?:دو|دي|دى)\s+(?:بارفيوم|برفيوم|بارفان|برفان|باررفيوم|بلرفيوم|بارفيم|بارفام|بارفوم|بيرفيوم|بارفيم)", "EDP"),
    (r"(?:اودي|اودو|اودى)\s+(?:بارفيوم|برفيوم|بارفان|بيرفيوم)", "EDP"),
    (r"de\s+parfum|de\s+parfan|de\s+parfu", "EDP"),
    (r"\bedp\b", "EDP"),
    (r"(?:او|أو)\s+(?:دو|دي|دى)\s+(?:تواليت|توليت|توايلت|تواليت)", "EDT"),
    (r"de\s+toilette|\bedt\b", "EDT"),
    (r"(?:اكستريه|اكستريت|اكسترايت)\s+(?:دو|دي|دى)\s+(?:بارفيوم|بارفان|برفيوم|برفان)", "Extrait"),
    (r"\bextrait\b", "Extrait"),
    (r"eau\s+de\s+cologne|\bedc\b|\bكولونيا?\b|\bكولون\b", "EDC"),
    (r"\bانتنس\b|\bانتينس\b|\bانتيس\b|\bإنتنس\b|\bintense\b", "Intense"),
    (r"\bابسولو\b|\bأبسولو\b|\babsolu\b|\bابسول\b", "Absolu"),
    (r"\bبارفيوم\b|\bبرفيوم\b|\bبارفان\b|\bبارفام\b|\bبيرفيوم\b|\bبارفوم\b|\bbrfom\b|\bparfum\b", "Parfum"),
]

WORD_MAP: dict = {
    "توم فرود":"tomford","تومس فورد":"tomford","tom ford":"tomford","توم فورد":"tomford",
    "فيرزاتشي":"versace","فيرساشي":"versace","versace":"versace","فيرساتشي":"versace",
    "اتيليه":"atelier","اتيلييه":"atelier","اتيليير":"atelier","اتيلير":"atelier","اتوليي":"atelier","atelier":"atelier",
    "جيفانشي":"givenchy","جيفينشي":"givenchy","givenchy":"givenchy","جيفنشي":"givenchy",
    "غيرلان":"guerlain","guerlain":"guerlain","جيرلان":"guerlain",
    "دولسي":"dng","دولتشي":"dng","dolce":"dng","جابانا":"dng","غابانا":"dng","gabbana":"dng",
    "ايف":"ysl","إيف":"ysl","يوسف":"ysl","سنت":"ysl","سانت":"ysl","لوران":"ysl",
    "ysl":"ysl","saint":"ysl","laurent":"ysl",
    "هوغو":"hugo","هيوجو":"hugo","hugo":"hugo",
    "باكو":"paco","رابان":"rabanne","rabanne":"rabanne","paco":"paco",
    "موسكينو":"moschino","moschino":"moschino",
    "ارماني":"armani","أرماني":"armani","armani":"armani","جورجيو":"armani","giorgio":"armani",
    "بربري":"burberry","burberry":"burberry","لاكوست":"lacoste","lacoste":"lacoste",
    "ديزل":"diesel","diesel":"diesel","تومي":"tommy","tommy":"tommy","هيلفيجر":"tommy",
    "امواج":"amouage","اميجي":"amouage","amouage":"amouage","اميدج":"amouage",
    "بولغاري":"bvlgari","بولجاري":"bvlgari","bvlgari":"bvlgari",
    "كارتيير":"cartier","كارتير":"cartier","cartier":"cartier",
    "لانكوم":"lancome","lancome":"lancome","لانفان":"lanvin","lanvin":"lanvin",
    "بالنسياغا":"balenciaga","balenciaga":"balenciaga",
    "شانيل":"chanel","chanel":"chanel","ديور":"dior","dior":"dior","كريستيان":"dior",
    "نارسيسو":"narciso","رودريغيز":"narciso","narciso":"narciso",
    "مانسيرا":"mancera","mancera":"mancera","بايريدو":"byredo","بيريدو":"byredo","byredo":"byredo",
    "انيشيو":"initio","إنيشيو":"initio","initio":"initio",
    "بنهالغونز":"penhal","penhaligons":"penhal",
    "افنان":"afnan","afnan":"afnan","كارولينا":"ch","هيريرا":"ch","carolina":"ch",
    "لابوراتوريو":"labolf","لابراتوريو":"labolf","أولفاتيفو":"labolf","اولفاتيفو":"labolf","olfativo":"labolf",
    "مارجيلا":"margiela","ميزون":"maison","maison":"maison","margiela":"margiela",
    "روشاس":"rochas","rochas":"rochas","فالنتينو":"valentino","valentino":"valentino",
    "اجنر":"aigner","aigner":"aigner","مياو":"miu","ميو":"miu","miu":"miu",
    "دافيدوف":"davidoff","davidoff":"davidoff","بربري":"burberry",
    "فيرتوس":"vertus","فيرتس":"vertus","vertus":"vertus",
    "سوسبيرو":"sospiro","sospiro":"sospiro",
    "تشيري":"cherry","cherry":"cherry","سويدي":"suede","سويد":"suede","suede":"suede",
    "سولاي":"soleil","soleil":"soleil","سوليل":"soleil",
    "بلانك":"blanc","بلان":"blanc","blanc":"blanc",
    "نيجه":"neige","neige":"neige","نيج":"neige",
    "توسكاني":"tuscan","تسكان":"tuscan","tuscan":"tuscan","توسكان":"tuscan",
    "ليدر":"leather","ليثر":"leather","leather":"leather","ليذر":"leather",
    "سنتال":"santal","صنتال":"santal","santal":"santal","صندال":"santal","سانتال":"santal",
    "جاسمين":"jasmin","ياسمينه":"jasmin","jasmine":"jasmin","jasmin":"jasmin","ياسمين":"jasmin",
    "امبر":"amber","امبير":"amber","amber":"amber","عنبر":"amber",
    "اود":"oud","oud":"oud","عود":"oud","وود":"oud",
    "ميسك":"musk","مسكي":"musk","musk":"musk","مسك":"musk",
    "نوير":"noir","noir":"noir","نوار":"noir",
    "بلوش":"blush","blush":"blush","بلاش":"blush",
    "روزي":"rose","rose":"rose","روز":"rose","ورد":"rose","وردة":"rose",
    "سموكي":"smoke","smoke":"smoke","سموك":"smoke",
    "وايتي":"white","white":"white","وايت":"white",
    "بوى":"bois","bois":"bois","بوا":"bois",
    "فانيل":"vanilla","فانيلي":"vanilla","vanilla":"vanilla","فانيله":"vanilla","فانيلا":"vanilla","فانيلى":"vanilla",
    "ازورا":"azure","azure":"azure","ازور":"azure",
    "ايبني":"ebene","ibeni":"ebene","ebene":"ebene",
    "فيجه":"fig","fig":"fig","فيج":"fig",
    "كافي":"cafe","cafe":"cafe","coffee":"cafe","كافيه":"cafe",
    "روبى":"ruby","ruby":"ruby","روبي":"ruby",
    "black":"black","بلاك":"black","gold":"gold","جولد":"gold","ذهبي":"gold",
    "بلوه":"blue","blue":"blue","bleu":"blue","بلو":"blue",
    "silk":"silk","سيلك":"silk","حرير":"silk",
    "سكندل":"scandal","scandal":"scandal","سكاندال":"scandal",
    "تنكا":"tonka","tonka":"tonka","تونكا":"tonka",
    "lilac":"lilac","ليلاك":"lilac","vetiver":"vetiver","فيتيفر":"vetiver",
    "patchouli":"patchouli","باتشولي":"patchouli",
    "bergamot":"bergamot","برغموت":"bergamot",
    "cedar":"cedar","سيدار":"cedar",
    "replica":"replica","ربليكا":"replica","ريبليكا":"replica",
    "darling":"darling","دارلينق":"darling","دارلينج":"darling",
    "paradise":"paradise","باراديس":"paradise","بارادايس":"paradise",
    "elixir":"elixir","اليكسير":"elixir","اليكزير":"elixir",
    "intense":"intense","انتينس":"intense",
    "extrait":"extrait","اكسترايت":"extrait","اكستريت":"extrait","إكستريت":"extrait",
    "للشعر":"","للجسم":"","معطر":"","لوشن":"","كريم":"","بودرة":"",
}

BRAND_CANONICAL = {
    "tomford":"توم فورد","versace":"فيرساتشي","atelier":"أتيليه",
    "givenchy":"جيفنشي","guerlain":"غيرلان","dng":"دولتشي آند غابانا",
    "ysl":"إيف سان لوران","hugo":"هوغو بوس","paco":"باكو رابان",
    "rabanne":"رابان","moschino":"موسكينو","armani":"أرماني",
    "burberry":"بربري","lacoste":"لاكوست","diesel":"ديزل","tommy":"تومي هيلفيجر",
    "amouage":"أمواج","bvlgari":"بولغاري","cartier":"كارتير",
    "lancome":"لانكوم","balenciaga":"بالنسياغا",
    "chanel":"شانيل","dior":"ديور","narciso":"نارسيسو رودريغيز",
    "mancera":"مانسيرا","byredo":"بايريدو","initio":"إنيشيو",
    "afnan":"أفنان","ch":"كارولينا هيريرا","margiela":"مارجيلا ميزون",
    "rochas":"روشاس","valentino":"فالنتينو","aigner":"أجنر","miu":"ميو ميو",
    "davidoff":"دافيدوف","vertus":"فيرتوس","sospiro":"سوسبيرو",
}

NOISE: frozenset = frozenset("""
عطر perfume fragrance نسائي رجالي للنساء للرجال للجنسين unisex
اصلي اورجينال original سبراي spray بخاخ من by de du le la les al el
for of and و اند تستر tester بدون كرتون ديمو demo no
مجموعة مجموعه طقم set gift هدايا هدية للشعر body للجسم eau
كريستيان christian لو la le les فرنسي يابانية اوروبية اروبية
اصدار edition limited ليميتد special خاص collector محدود new جديد
""".split())

SIZE_VALUES: frozenset = frozenset(
    "10 15 20 25 30 40 50 60 70 75 80 90 100 125 150 200 250 500".split()
)

SIZE_RE = re.compile(r"(\d+(?:\.\d+)?)\s*(?:ml|مل|مللي|g|gr|gm|جرام)", re.I)
OZ_RE   = re.compile(r"(\d+(?:\.\d+)?)\s*(?:fl\.?oz|oz)\b", re.I)

# ══════════════════════════════════════════════════════
#  V14 NORMALIZATION FUNCTIONS
# ══════════════════════════════════════════════════════

def arabic_base(text: str) -> str:
    t = unicodedata.normalize("NFKC", str(text))
    t = re.sub(r"[\u064B-\u065F\u0670\u0671]", "", t)
    t = re.sub(r"[أإآ]", "ا", t)
    t = t.replace("ة","ه").replace("ى","ي")
    t = re.sub(r"[_\-،,]+", " ", t)
    return re.sub(r"\s+", " ", t).lower().strip()

def replace_concs(text: str) -> str:
    for pattern, code in CONC_PATTERNS:
        text = re.sub(pattern, f" {code} ", text, flags=re.I)
    return re.sub(r"\s+", " ", text).strip()

def replace_variants(text: str) -> str:
    return " ".join(WORD_MAP.get(w, w) for w in text.split())

def full_norm(raw: str) -> str:
    t = arabic_base(raw)
    t = replace_concs(t)
    t = replace_variants(t)
    return re.sub(r"\s+", " ", t).strip()

def extract_size(text: str):
    sizes = [float(x) for x in SIZE_RE.findall(str(text))]
    sizes += [round(float(x)*29.574,1) for x in OZ_RE.findall(str(text))]
    if not sizes: return None
    m = max(sizes)
    return m if m > MIN_SIZE_ML else None

def extract_concentration(normed: str) -> str:
    for code in ("Extrait","EDP","Parfum","EDT","EDC","Intense","Absolu"):
        if code in normed: return code
    return "Unknown"

def extract_type(raw: str) -> str:
    t = raw.lower()
    if re.search(r"\btester\b|تستر|بدون\s*كرتون|ديمو|\bdemo\b|\bno\s*box\b", t): return "tester"
    if re.search(r"\bset\b|طقم|مجموعه|مجموعة|\bgift\s*set\b|\bkit\b", t): return "set"
    if re.search(r"\bhair\b|شعر", t): return "hair"
    if re.search(r"\bbody\s*mist\b|معطر\s*جسم|\bbody\s*spray\b", t): return "body_mist"
    if re.search(r"\bshower\s*gel\b|شاور\s*جل", t): return "shower"
    if re.search(r"\blotion\b|لوشن|\bcream\b|كريم", t): return "lotion"
    return "regular"

def get_core(raw: str) -> str:
    t = full_norm(raw)
    t = SIZE_RE.sub(" ", t)
    t = OZ_RE.sub(" ", t)
    t = re.sub(r"\b\d+(?:\.\d+)?\b", " ", t)
    for code in ("EDP","EDT","Extrait","Parfum","EDC","Intense","Absolu",
                 "edp","edt","extrait","parfum","edc","intense","absolu"):
        t = re.sub(r"\b"+re.escape(code)+r"\b", " ", t, flags=re.I)
    words = [w for w in t.split() if w not in NOISE and len(w)>1]
    return re.sub(r"\s+", " ", " ".join(words)).strip()

def get_sig_numbers(raw: str) -> frozenset:
    nums = re.findall(r"\b\d{2,}\b", str(raw))
    return frozenset(n for n in nums if n not in SIZE_VALUES)

def _sz_ok(s1, s2, tol=0.07) -> bool:
    if s1 is None and s2 is None: return True
    if s1 is None or s2 is None: return False
    try: return abs(float(s1)-float(s2)) <= max(float(s1),float(s2))*tol
    except: return False

def is_same_product(comp_raw, our_raw, comp_sz, our_sz):
    if not _sz_ok(comp_sz, our_sz):
        return False, f"حجم مختلف ({comp_sz}مل ≠ {our_sz}مل)"
    comp_full = full_norm(comp_raw); our_full = full_norm(our_raw)
    c_conc = extract_concentration(comp_full); o_conc = extract_concentration(our_full)
    if c_conc != "Unknown" and o_conc != "Unknown" and c_conc != o_conc:
        return False, f"تركيز مختلف ({c_conc} ≠ {o_conc})"
    if extract_type(comp_raw) != extract_type(our_raw):
        return False, "نوع مختلف"
    nc = get_sig_numbers(comp_raw); no = get_sig_numbers(our_raw)
    if nc and no and not (nc & no): return False, "رقم مختلف"
    comp_base = arabic_base(comp_raw); our_base = arabic_base(our_raw)
    comp_core = get_core(comp_raw); our_core = get_core(our_raw)
    if len(comp_core.replace(" ",""))<3 or len(our_core.replace(" ",""))<3:
        return False, "اسم جوهري قصير"
    wc = frozenset(w for w in comp_core.split() if len(w)>3)
    wo = frozenset(w for w in our_core.split() if len(w)>3)
    if wc and wo:
        extra = wc.symmetric_difference(wo); total = len(wc|wo)
        if total>0 and len(extra)/total>0.45 and len(extra)>=2:
            return False, f"كلمات زائدة: {extra}"
    m1=fuzz.ratio(comp_base,our_base); m2=fuzz.token_sort_ratio(comp_base,our_base)
    m3=fuzz.ratio(comp_full,our_full); m4=fuzz.token_sort_ratio(comp_full,our_full)
    m5=(100.0*len(wc&wo)/len(wc|wo)) if (wc and wo) else 0.0
    if m4>=88 and m2>=78: return True, f"تطابق عالي (م4={m4:.0f}%)"
    if m2>=92 and m1>=85: return True, f"تطابق تام (م2={m2:.0f}%)"
    if m4>=92 and m3>=85: return True, f"تطابق بعد تطبيع (م4={m4:.0f}%)"
    if m5>=80 and m4>=82: return True, f"تطابق كلمات ({m5:.0f}%)"
    if m4>=95: return True, f"نفس الكلمات (م4={m4:.0f}%)"
    if m4>=85 and m5>=65: return True, f"تطابق كافٍ (م4={m4:.0f}%)"
    return False, f"مختلف (أقرب: {max(m1,m2,m3,m4,m5):.0f}%)"

class StoreIndex:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy().reset_index(drop=True)
        self.df["_sz"]   = self.df["product_name"].apply(extract_size)
        self.df["_core"] = self.df["product_name"].apply(get_core)
        self.df["_full"] = self.df["product_name"].apply(full_norm)
        self.cores = self.df["_core"].tolist()
        self.fulls = self.df["_full"].tolist()

    def find(self, comp_raw: str, comp_sz):
        comp_core = get_core(comp_raw); comp_full = full_norm(comp_raw)
        if not comp_core or len(comp_core.replace(" ",""))<2:
            return None, 0.0, "اسم فارغ"
        hits_core = rfp.extract(comp_core, self.cores, scorer=fuzz.token_sort_ratio, limit=8, score_cutoff=50)
        hits_full = rfp.extract(comp_full, self.fulls, scorer=fuzz.token_sort_ratio, limit=8, score_cutoff=50)
        seen: set = set(); candidates: list = []
        for _, sc, idx in (hits_core + hits_full):
            if idx not in seen:
                seen.add(idx); candidates.append((sc, idx))
        candidates.sort(reverse=True)
        for _, idx in candidates[:8]:
            our_row = self.df.iloc[idx]
            matched, reason = is_same_product(comp_raw, our_row["product_name"], comp_sz, our_row["_sz"])
            if matched: return our_row, candidates[0][0], reason
        best_sc = candidates[0][0] if candidates else 0.0
        return None, best_sc, f"غير موجود (أقرب: {best_sc:.0f}%)"

# ══════════════════════════════════════════════════════
#  DATA LOADING
# ══════════════════════════════════════════════════════

def _read_csv(path):
    for enc in ("utf-8","utf-8-sig","windows-1256","latin-1"):
        try: return pd.read_csv(path, dtype=str, encoding=enc)
        except: continue
    raise ValueError(f"تعذّر قراءة: {path}")

@st.cache_data(show_spinner=False)
def load_our_store(paths: tuple) -> pd.DataFrame:
    frames = []
    for p in paths:
        path = Path(p)
        if not path.exists(): continue
        try:
            df = _read_csv(path)
            # Skip header row if first col is "بيانات المنتج"
            if str(df.iloc[0,0]).strip() in ["بيانات المنتج","No."]:
                df = pd.read_csv(path, dtype=str, encoding="utf-8-sig", skiprows=1)
            df.columns = df.columns.str.strip()
            df.rename(columns={"أسم المنتج":"product_name","سعر المنتج":"price",
                                "رمز المنتج sku":"sku","صورة المنتج":"image_url",
                                "تصنيف المنتج":"category","الماركة":"brand"}, inplace=True)
            frames.append(df)
        except Exception as e:
            st.warning(f"خطأ في {path.name}: {e}")
    if not frames: return pd.DataFrame()
    combined = pd.concat(frames, ignore_index=True)
    combined.dropna(subset=["product_name"], inplace=True)
    combined["product_name"] = combined["product_name"].str.strip()
    # Extract first image URL from comma-separated list
    if "image_url" in combined.columns:
        combined["image_url"] = combined["image_url"].apply(
            lambda x: str(x).split(",")[0].strip() if pd.notna(x) else "")
    return combined.reset_index(drop=True)

@st.cache_data(show_spinner=False)
def load_competitor(path_str: str, name: str):
    path = Path(path_str)
    if not path.exists(): return None
    try:
        df = _read_csv(path)
        df.columns = df.columns.str.strip()
        df.rename(columns={
            "styles_productCard__name__pakbB": "product_name",
            "w-full src": "image_url",
            "text-sm-2": "price",
            "abs-size href": "product_url",
        }, inplace=True)
        if "product_name" not in df.columns:
            cols = df.columns.tolist()
            if len(cols)>=1: df.rename(columns={cols[0]:"product_url"}, inplace=True)
            # find name col
            for c in df.columns:
                if df[c].str.len().mean() > 15 and not df[c].str.startswith("http").mean() > 0.5:
                    df.rename(columns={c:"product_name"}, inplace=True); break
        if "product_name" not in df.columns:
            return None
        keep = [c for c in ["product_name","image_url","price","product_url"] if c in df.columns]
        df = df[keep].copy()
        df["competitor"] = name
        df.dropna(subset=["product_name"], inplace=True)
        df["product_name"] = df["product_name"].str.strip()
        df = df[df["product_name"].str.len()>3].reset_index(drop=True)
        return df
    except Exception as e:
        return None

@st.cache_data(show_spinner=False)
def load_categories(path_str: str) -> list:
    path = Path(path_str)
    if not path.exists(): return []
    try:
        df = _read_csv(path)
        df.columns = df.columns.str.strip()
        cats = df.iloc[:,0].dropna().tolist()
        mains = df.iloc[:,2].dropna().tolist() if len(df.columns)>2 else []
        result = []
        for i, cat in enumerate(cats):
            main = mains[i] if i < len(mains) else ""
            if main and str(main).strip():
                result.append(f"{main} > {cat}")
            else:
                result.append(str(cat))
        return sorted(set(result))
    except: return []

@st.cache_data(show_spinner=False)
def load_brands(path_str: str) -> dict:
    path = Path(path_str)
    if not path.exists(): return {}
    try:
        df = _read_csv(path)
        df.columns = df.columns.str.strip()
        brands = {}
        for _, row in df.iterrows():
            name = str(row.iloc[0]).strip()
            desc = str(row.iloc[1]).strip() if len(df.columns)>1 else ""
            brands[name] = desc
        return brands
    except: return {}

# ══════════════════════════════════════════════════════
#  BRAND / CATEGORY DETECTION
# ══════════════════════════════════════════════════════

def detect_brand_from_name(product_name: str, brands_dict: dict) -> str:
    """Detect brand from product name using WORD_MAP + brands_dict"""
    normed = full_norm(product_name)
    # Check canonical brands from WORD_MAP
    for word in normed.split():
        if word in BRAND_CANONICAL:
            display = BRAND_CANONICAL[word]
            # Try to find matching entry in brands_dict
            for brand_key in brands_dict:
                if display in brand_key or word.lower() in brand_key.lower():
                    return brand_key
            return display
    # Direct search in brands_dict
    name_lower = product_name.lower()
    for brand_key in brands_dict:
        # Extract English name from "عربي | English" format
        parts = brand_key.split("|")
        for part in parts:
            part = part.strip()
            if part.lower() in name_lower or name_lower in part.lower():
                return brand_key
    return ""

def suggest_category(product_name: str, categories: list) -> str:
    """Suggest category based on product name keywords"""
    name_lower = product_name.lower()
    name_ar = product_name
    # Type detection
    if re.search(r"تستر|tester|بدون كرتون|ديمو", name_lower):
        prefix = "عطور التستر"
    elif re.search(r"طقم|set|مجموعة", name_lower):
        prefix = "مجموعات وأطقم هدايا"
    elif re.search(r"شعر|hair", name_lower):
        prefix = "للشعر والجسم"
    elif re.search(r"لوشن|lotion|body mist|معطر جسم", name_lower):
        prefix = "للشعر والجسم"
    elif re.search(r"نيش|niche|exclusive", name_lower):
        prefix = "عطور النيش"
    elif re.search(r"نسائ|للنساء|women|woman|feminine|نسائية", name_lower):
        prefix = "العطور > عطور نسائية"
    elif re.search(r"رجال|للرجال|men|man|masculine|رجالي", name_lower):
        prefix = "العطور > عطور رجالية"
    else:
        prefix = "العطور"
    # Find matching category
    for cat in categories:
        if prefix in cat:
            return cat
    if categories:
        for cat in categories:
            if "عطور" in cat and "نسائية" in cat and "نسائ" in product_name:
                return cat
            if "عطور" in cat and "رجالية" in cat and "رجال" in product_name:
                return cat
    return prefix

def extract_brand_canonical(product_name: str) -> str:
    """Return canonical brand name for grouping"""
    normed = full_norm(product_name)
    for word in normed.split():
        if word in BRAND_CANONICAL:
            return BRAND_CANONICAL[word].split(" | ")[0]
    return "أخرى"

def prod_key(name: str, sz) -> str:
    return hashlib.md5(f"{get_core(name)}_{sz}".encode()).hexdigest()[:10]

# ══════════════════════════════════════════════════════
#  DEDUPLICATION (from v14)
# ══════════════════════════════════════════════════════

def deduplicate_missing(rows: list) -> list:
    groups: dict = defaultdict(list)
    for r in rows:
        core_key = get_core(r["name"])
        sz_bucket = round((r["sz"] or 0)/5)*5
        key = (core_key, sz_bucket)
        groups[key].append(r)
    deduped = []
    for key, group in groups.items():
        rep = max(group, key=lambda x: len(x["name"]))
        comp_names = sorted(set(g["competitor"] for g in group))
        comp_prices = []
        for g in group:
            try:
                p = float(re.sub(r"[^\d.]", "", str(g.get("price","") or "")))
                comp_prices.append(p)
            except: pass
        entry = {
            "name": rep["name"],
            "image": rep.get("image",""),
            "price": rep.get("price",""),
            "sz": rep["sz"],
            "competitor": rep["competitor"],
            "all_competitors": " | ".join(comp_names),
            "competitor_count": len(comp_names),
            "min_price": f"{min(comp_prices):.0f}" if comp_prices else "",
            "max_price": f"{max(comp_prices):.0f}" if comp_prices else "",
            "reason": rep.get("reason",""),
            "score": rep.get("score",0),
            "brand_group": extract_brand_canonical(rep["name"]),
        }
        deduped.append(entry)
    deduped.sort(key=lambda x: (-x["competitor_count"], x["name"]))
    return deduped

# ══════════════════════════════════════════════════════
#  CLAUDE API — DESCRIPTION GENERATION
# ══════════════════════════════════════════════════════

EXPERT_SYSTEM_PROMPT = """أنت خبير عالمي في كتابة أوصاف منتجات العطور محسّنة لمحركات البحث التقليدية (Google SEO) ومحركات بحث الذكاء الصناعي (GEO/AIO). تعمل حصرياً لمتجر "مهووس" (Mahwous) - الوجهة الأولى للعطور الفاخرة في السعودية.

**مهمتك:** كتابة وصف منتج عطور شامل باللغة العربية الفصحى بأسلوب راقٍ، عاطفي، وتسويقي مقنع.

**البنية الإلزامية للوصف (1200-1500 كلمة بتنسيق HTML):**

1. **الفقرة الافتتاحية** (H1 = اسم المنتج الكامل): جملة عاطفية قوية، الكلمة الرئيسية في أول 50 كلمة، دعوة مبكرة للشراء.

2. **تفاصيل المنتج** (H2): قائمة نقطية — الماركة، المصمم، الجنس، العائلة العطرية، الحجم، التركيز، سنة الإصدار.

3. **رحلة العطر: الهرم العطري** (H2): النفحات العليا، الوسطى، الأساسية — وصف حسي عاطفي بالمكونات وليس مجرد قائمة.

4. **لماذا تختار هذا العطر؟** (H2): 4-6 نقاط، كل نقطة تبدأ بـ <strong>كلمة مفتاحية</strong>، تركز على الفوائد.

5. **متى وأين ترتدي هذا العطر؟** (H2): الفصول المناسبة، الأوقات المثالية، المناسبات، الفئة العمرية.

6. **لمسة خبير من مهووس** (H2): تقييم احترافي بضمير "نحن"، ثبات بالساعات، مقارنات، توصية.

7. **الأسئلة الشائعة FAQ** (H2): 6-8 أسئلة حوارية، الإجابة 50-80 كلمة، تكرار الكلمة المفتاحية.

8. **الفقرة الختامية** (H2 = "عالمك العطري يبدأ من مهووس"): الكلمة الرئيسية مرتين، "أصلي 100%"، "ضمان الأصالة"، دعوة قوية للشراء.

**قواعد الأسلوب:**
- لا إيموجي
- استخدم <strong> للكلمات المفتاحية المهمة
- أسلوب مزيج: راقٍ (40%) + ودود (25%) + عاطفي (20%) + تسويقي (15%)
- الشعار الختامي: "عالمك العطري يبدأ من مهووس"

**أرجع الوصف بتنسيق HTML فقط، بدون أي نص خارج HTML.**"""

def generate_description(product_info: dict) -> str:
    """Call Claude API to generate product description"""
    prompt = f"""اكتب وصفاً احترافياً لمنتج العطر التالي:

- اسم المنتج الكامل: {product_info.get('name', '')}
- الماركة: {product_info.get('brand', 'غير محدد')}
- الحجم: {product_info.get('sz', '')} مل
- التركيز: {product_info.get('concentration', 'غير محدد')}
- السعر في متجرنا: {product_info.get('price', '')} ر.س
- التصنيف: {product_info.get('category', '')}
- جنس العطر (إذا واضح): {product_info.get('gender', 'غير محدد')}

اكتب الوصف الكامل بتنسيق HTML كما هو محدد في تعليماتك."""

    try:
        response = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={"Content-Type": "application/json"},
            json={
                "model": "claude-sonnet-4-6",
                "max_tokens": 4096,
                "system": EXPERT_SYSTEM_PROMPT,
                "messages": [{"role": "user", "content": prompt}]
            },
            timeout=90
        )
        if response.status_code == 200:
            data = response.json()
            return data["content"][0]["text"]
        else:
            return f"<p>خطأ في API: {response.status_code} — {response.text[:200]}</p>"
    except Exception as e:
        return f"<p>خطأ في الاتصال: {str(e)}</p>"

# ══════════════════════════════════════════════════════
#  EXPORT
# ══════════════════════════════════════════════════════

SALLA_COLS = [
    "النوع ","أسم المنتج","تصنيف المنتج","صورة المنتج","وصف صورة المنتج",
    "نوع المنتج","سعر المنتج","الوصف","هل يتطلب شحن؟","رمز المنتج sku",
    "سعر التكلفة","السعر المخفض","تاريخ بداية التخفيض","تاريخ نهاية التخفيض",
    "اقصي كمية لكل عميل","إخفاء خيار تحديد الكمية","اضافة صورة عند الطلب",
    "الوزن","وحدة الوزن","الماركة","العنوان الترويجي","تثبيت المنتج","الباركود",
    "السعرات الحرارية","MPN","GTIN","خاضع للضريبة ؟","سبب عدم الخضوع للضريبة",
    "[1] الاسم","[1] النوع","[1] القيمة","[1] الصورة / اللون",
    "[2] الاسم","[2] النوع","[2] القيمة","[2] الصورة / اللون",
    "[3] الاسم","[3] النوع","[3] القيمة","[3] الصورة / اللون",
]

def build_export_row(product: dict) -> dict:
    row = {c:"" for c in SALLA_COLS}
    try: weight = round(float(product.get("sz",0) or 0)/1000, 3)
    except: weight = ""
    row["النوع "]         = "منتج"
    row["أسم المنتج"]    = product.get("name","")
    row["تصنيف المنتج"]  = product.get("category","")
    row["صورة المنتج"]   = product.get("image","")
    row["نوع المنتج"]    = "منتج جاهز"
    row["سعر المنتج"]    = product.get("price","")
    row["الوصف"]         = product.get("description","")
    row["هل يتطلب شحن؟"] = "نعم"
    row["الوزن"]         = weight
    row["وحدة الوزن"]    = "kg"
    row["الماركة"]       = product.get("brand","")
    row["خاضع للضريبة ؟"] = "نعم"
    return row

def to_csv_bytes(rows: list) -> bytes:
    # Header row like منتج_جديد.csv
    df_header = pd.DataFrame([["بيانات المنتج"] + [""]*( len(SALLA_COLS)-1)], columns=SALLA_COLS)
    df_data   = pd.DataFrame(rows, columns=SALLA_COLS)
    combined  = pd.concat([df_header, df_data], ignore_index=True)
    buf = io.StringIO()
    combined.to_csv(buf, index=False, encoding="utf-8-sig")
    return buf.getvalue().encode("utf-8-sig")

# ══════════════════════════════════════════════════════
#  SESSION STATE INIT
# ══════════════════════════════════════════════════════

def init_state():
    defaults = {
        "not_avail": [], "avail": [], "engine_done": False,
        "approved": set(), "rejected": set(),
        "descriptions": {}, "product_edits": {},
        "page_miss": 0, "page_avail": 0,
        "brand_filter": "الكل", "view_mode": "missing",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()

# ══════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════

with st.sidebar:
    st.markdown("""<div class="logo-title">
        <div class="logo-t">🌹 مهووس</div>
        <div class="logo-s">محرك المنتجات والمراجعة البصرية</div>
    </div>""", unsafe_allow_html=True)
    st.divider()

    st.subheader("📂 ملفات متجرنا")
    our_parts = st.text_area(
        "مسارات ملفات متجرنا (سطر لكل ملف)",
        value="\n".join([
            "متجرنا_مهووس_جزء_1.csv",
            "متجرنا_مهووس_جزء_2.csv",
            "متجرنا_مهووس_جزء_3.csv",
            "متجرنا_مهووس_جزء_4.csv",
        ]), height=100
    )

    st.subheader("🏪 ملفات المنافسين")
    comp_default = "\n".join([
        "عالم_جيفنشي|متجر_عالم_جيفنشي_بكل_الاعمدة_السعر_والصور.csv",
        "ساراء_ميكاب|متجر_ساراء_ميكاب.csv",
        "عالم_جيفنشي_قديم|متجر_عالم_جيفنشي_للعطور.csv",
        "خبير_العطور|متجر_خبير_العطور.csv",
        "سارا_ستور|متجر_سارا_ستور.csv",
        "افنوس|متجر_افنوس.csv",
        "اريج_امواج|متجر_اريج_امواج.csv",
        "كاندي_نيش|متجر_كاندي_نيش.csv",
        "حنان|متجر_حنان.csv",
        "فنيلا|متجر_فنيلا.csv",
        "الفاخرة|متجر_الفاخرة_للعطور.csv",
        "سارا_ميكاب_قديم|متجر_سارا_ميكاب.csv",
        "نواعم|متجر_نواعم.csv",
        "سعيد_صلاح|متجر_سعيد_صلاح.csv",
        "لي_سانتو|متجر_لي_سانتو.csv",
    ])
    comp_text = st.text_area("اسم|مسار_الملف (سطر لكل منافس)",
                             value=comp_default, height=260)

    st.subheader("⚙️ ملفات مساعدة")
    cats_file   = st.text_input("ملف التصنيفات",   value="تصنيفات_مهووس.csv")
    brands_file = st.text_input("ملف الماركات",    value="ماركات_مهووس.csv")

    st.divider()
    run_btn = st.button("🚀 تشغيل محرك المطابقة", type="primary", use_container_width=True)
    if st.session_state.engine_done:
        not_avail_dedup = deduplicate_missing(st.session_state.not_avail)
        st.success(f"✅ {len(not_avail_dedup):,} منتج مفقود  |  {len(st.session_state.avail):,} مطابق")

# ══════════════════════════════════════════════════════
#  RUN ENGINE
# ══════════════════════════════════════════════════════

if run_btn:
    our_paths = tuple(p.strip() for p in our_parts.strip().split("\n") if p.strip())
    comp_pairs = []
    for line in comp_text.strip().split("\n"):
        line = line.strip()
        if "|" in line:
            parts = line.split("|", 1)
            comp_pairs.append((parts[0].strip(), parts[1].strip()))

    with st.spinner("جارٍ تحميل البيانات..."):
        our_df = load_our_store(our_paths)
        if our_df.empty:
            st.error("❌ لم يُعثر على ملفات متجرنا")
            st.stop()
        st.info(f"✅ متجرنا: {len(our_df):,} منتج")

    comp_frames = []
    for name, path in comp_pairs:
        cdf = load_competitor(path, name)
        if cdf is not None:
            comp_frames.append(cdf)

    if not comp_frames:
        st.error("❌ لا توجد ملفات منافسين صالحة")
        st.stop()

    comp_all = pd.concat(comp_frames, ignore_index=True)
    st.info(f"✅ المنافسون: {len(comp_all):,} منتج من {len(comp_frames)} متجر")

    # Build index
    with st.spinner("بناء فهرس الخبير..."):
        index = StoreIndex(our_df)

    # Build our_name→image lookup
    our_image_lookup = {}
    if "image_url" in our_df.columns and "product_name" in our_df.columns:
        for _, row in our_df.iterrows():
            our_image_lookup[str(row["product_name"]).strip()] = str(row.get("image_url",""))

    not_avail = []; avail = []; skipped = 0
    progress = st.progress(0)
    status_txt = st.empty()
    total_rows = len(comp_all)

    for i, (_, row) in enumerate(comp_all.iterrows(), 1):
        if i % 50 == 0:
            progress.progress(min(i/total_rows, 1.0))
            status_txt.text(f"فحص {i:,} / {total_rows:,}  |  غير متوفر: {len(not_avail):,}")

        name = str(row.get("product_name","")).strip()
        if len(name)<3: skipped+=1; continue
        sz = extract_size(name)
        if sz is None: skipped+=1; continue

        match, score, reason = index.find(name, sz)
        entry = {
            "name": name,
            "image": str(row.get("image_url","")),
            "price": str(row.get("price","")),
            "sz": sz,
            "competitor": str(row.get("competitor","")),
            "reason": reason,
            "score": round(score,1),
            "brand_group": extract_brand_canonical(name),
        }
        if match is not None:
            entry["our_name"]  = match["product_name"]
            entry["our_image"] = our_image_lookup.get(str(match["product_name"]).strip(),"")
            entry["our_price"] = str(match.get("price",""))
            avail.append(entry)
        else:
            not_avail.append(entry)

    progress.progress(1.0)
    status_txt.empty()

    st.session_state.not_avail    = not_avail
    st.session_state.avail        = avail
    st.session_state.engine_done  = True
    st.session_state.approved     = set()
    st.session_state.rejected     = set()
    st.session_state.descriptions = {}
    st.session_state.page_miss    = 0
    dedup_count = len(deduplicate_missing(not_avail))
    st.success(f"🎉 اكتمل! غير متوفر: {dedup_count:,} منتج  |  متوفر: {len(avail):,}  |  تجاهل: {skipped:,}")
    st.balloons()

# ══════════════════════════════════════════════════════
#  MAIN TABS
# ══════════════════════════════════════════════════════

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 لوحة التحكم",
    "👁️ المراجعة البصرية",
    "✍️ توليد الأوصاف",
    "📤 التصدير",
])

# ─── TAB 1: DASHBOARD ────────────────────────────────

with tab1:
    if not st.session_state.engine_done:
        st.markdown("""<div style="text-align:center;padding:4rem;">
            <div style="font-size:3rem;">🌹</div>
            <div style="font-size:1.3rem;font-weight:700;color:var(--gold2);margin:.5rem 0;">مرحباً بك في محرك مهووس</div>
            <div style="color:var(--muted);">اضغط "تشغيل محرك المطابقة" من الشريط الجانبي للبدء</div>
        </div>""", unsafe_allow_html=True)
    else:
        not_avail_dedup = deduplicate_missing(st.session_state.not_avail)
        approved_cnt = len(st.session_state.approved)
        rejected_cnt = len(st.session_state.rejected)
        desc_cnt     = len(st.session_state.descriptions)

        # Metrics row
        m = st.columns(5)
        metrics = [
            (len(not_avail_dedup), "منتج مفقود (بعد إزالة التكرار)", "🔴"),
            (len(st.session_state.avail), "منتج مطابق مؤكد", "✅"),
            (approved_cnt, "تمت الموافقة", "👍"),
            (rejected_cnt, "تم التجاهل", "👎"),
            (desc_cnt, "أوصاف جاهزة", "✍️"),
        ]
        for col, (val, lbl, icon) in zip(m, metrics):
            with col:
                st.markdown(f"""<div class="metric-card">
                    <div class="metric-val">{val:,}</div>
                    <div class="metric-lbl">{icon} {lbl}</div>
                </div>""", unsafe_allow_html=True)

        st.divider()

        # Brand breakdown
        st.markdown('<div class="sec-title">📦 توزيع المنتجات المفقودة حسب الماركة</div>', unsafe_allow_html=True)
        brand_counts = defaultdict(int)
        for r in not_avail_dedup:
            brand_counts[r.get("brand_group","أخرى")] += 1
        brand_df = pd.DataFrame(
            sorted(brand_counts.items(), key=lambda x:-x[1]),
            columns=["الماركة","عدد المنتجات المفقودة"]
        )
        st.dataframe(brand_df, hide_index=True, use_container_width=True)

        st.divider()
        # Competitor breakdown
        st.markdown('<div class="sec-title">🏪 توزيع المنتجات المفقودة حسب المنافس</div>', unsafe_allow_html=True)
        comp_counts = defaultdict(int)
        for r in st.session_state.not_avail:
            comp_counts[r["competitor"]] += 1
        comp_df = pd.DataFrame(
            sorted(comp_counts.items(), key=lambda x:-x[1]),
            columns=["المنافس","منتجات غير موجودة لدينا"]
        ).reset_index(drop=True)
        st.dataframe(comp_df, hide_index=True, use_container_width=True)

# ─── TAB 2: VISUAL REVIEW ────────────────────────────

with tab2:
    if not st.session_state.engine_done:
        st.info("▶️ شغّل المحرك أولاً من الشريط الجانبي")
    else:
        # Load categories & brands for UI
        categories = load_categories(cats_file)
        brands_dict = load_brands(brands_file)

        view_col, _, filter_col = st.columns([3,1,4])
        with view_col:
            view_mode = st.radio("العرض", ["🔴 منتجات مفقودة", "✅ تحقق من التطابق"],
                                 horizontal=True, key="view_radio")
        
        not_avail_dedup = deduplicate_missing(st.session_state.not_avail)
        
        # Brand filter
        all_brands = sorted(set(r.get("brand_group","أخرى") for r in not_avail_dedup))
        with filter_col:
            brand_filter = st.selectbox("🔍 تصفية حسب الماركة",
                                        ["الكل"] + all_brands, key="brand_sel")

        # ═══ MISSING PRODUCTS VIEW ═══
        if "مفقودة" in view_mode:
            filtered = [r for r in not_avail_dedup
                        if brand_filter == "الكل" or r.get("brand_group") == brand_filter]

            # Stats bar
            pending  = [r for r in filtered if prod_key(r["name"],r["sz"]) not in st.session_state.approved and prod_key(r["name"],r["sz"]) not in st.session_state.rejected]
            approved = [r for r in filtered if prod_key(r["name"],r["sz"]) in st.session_state.approved]
            st.markdown(f"""
            <div style="display:flex;gap:12px;margin-bottom:1rem;flex-wrap:wrap;">
              <span class="badge badge-cnt">🔴 إجمالي: {len(filtered)}</span>
              <span class="badge badge-grn">👍 موافق: {len(approved)}</span>
              <span class="badge badge-cnt">⏳ معلق: {len(pending)}</span>
            </div>""", unsafe_allow_html=True)

            # Group by brand
            by_brand: dict = defaultdict(list)
            for r in filtered:
                by_brand[r.get("brand_group","أخرى")].append(r)

            PAGE_SIZE = 12
            for brand_name, products in sorted(by_brand.items(), key=lambda x: -len(x[1])):
                st.markdown(f'<div class="brand-hdr">🏷️ {brand_name} &nbsp;<span class="badge badge-cnt">{len(products)}</span></div>', unsafe_allow_html=True)

                # Paginate per brand if too many
                show_all = st.checkbox(f"عرض الكل ({len(products)})", key=f"showall_{brand_name}")
                products_show = products if show_all else products[:PAGE_SIZE]

                cols = st.columns(3)
                for idx, prod in enumerate(products_show):
                    pkey = prod_key(prod["name"], prod["sz"])
                    is_approved = pkey in st.session_state.approved
                    is_rejected = pkey in st.session_state.rejected
                    card_cls = "pcard approved" if is_approved else ("pcard rejected" if is_rejected else "pcard")

                    with cols[idx % 3]:
                        with st.container():
                            # Image
                            img_url = prod.get("image","")
                            if img_url and img_url.startswith("http"):
                                st.image(img_url, use_container_width=True)
                            else:
                                st.markdown('<div style="height:160px;background:var(--surf);border-radius:8px;display:flex;align-items:center;justify-content:center;color:var(--muted);">لا صورة</div>', unsafe_allow_html=True)
                            
                            # Info
                            conc = extract_concentration(full_norm(prod["name"]))
                            st.markdown(f"""
                            <div class="pname">{prod["name"]}</div>
                            <div style="display:flex;gap:6px;flex-wrap:wrap;margin:.3rem 0;">
                              <span class="badge badge-gold">{prod.get('sz','')} مل</span>
                              {"" if conc=="Unknown" else f'<span class="badge badge-cnt">{conc}</span>'}
                              <span class="badge badge-{"grn" if prod["competitor_count"]>=3 else "cnt"}">{prod["competitor_count"]} منافسين</span>
                            </div>
                            <div class="pcomp">📦 {prod.get("all_competitors","")}</div>
                            <div style="margin:.3rem 0;">
                              <span class="pprice">💰 {prod.get("min_price","")}{"–"+prod.get("max_price","") if prod.get("max_price","")!=prod.get("min_price","") else ""} ر.س</span>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Action buttons
                            if is_approved:
                                if st.button("↩️ إلغاء الموافقة", key=f"unapprove_{pkey}", use_container_width=True):
                                    st.session_state.approved.discard(pkey)
                                    st.rerun()
                            elif is_rejected:
                                if st.button("↩️ استرداد", key=f"unreject_{pkey}", use_container_width=True):
                                    st.session_state.rejected.discard(pkey)
                                    st.rerun()
                            else:
                                b1, b2 = st.columns(2)
                                with b1:
                                    if st.button("✅ أضف", key=f"app_{pkey}", use_container_width=True, type="primary"):
                                        st.session_state.approved.add(pkey)
                                        # Store full product data for description tab
                                        if pkey not in st.session_state.product_edits:
                                            st.session_state.product_edits[pkey] = {
                                                **prod,
                                                "category": suggest_category(prod["name"], categories),
                                                "brand": detect_brand_from_name(prod["name"], brands_dict),
                                                "concentration": conc,
                                                "gender": "نسائي" if re.search(r"نسائ|للنساء", prod["name"]) else ("رجالي" if re.search(r"رجال|للرجال", prod["name"]) else "للجنسين"),
                                            }
                                        st.rerun()
                                with b2:
                                    if st.button("❌ تجاهل", key=f"rej_{pkey}", use_container_width=True):
                                        st.session_state.rejected.add(pkey)
                                        st.rerun()

                if not show_all and len(products) > PAGE_SIZE:
                    st.caption(f"... و {len(products)-PAGE_SIZE} منتج آخر — اضغط 'عرض الكل' لرؤيتها")

        # ═══ MATCH VERIFICATION VIEW ═══
        else:
            avail = st.session_state.avail
            avail_filtered = [r for r in avail
                              if brand_filter == "الكل" or r.get("brand_group") == brand_filter]

            st.markdown(f"""<div style="margin-bottom:1rem;">
              <span class="badge badge-cnt">✅ إجمالي التطابقات: {len(avail_filtered)}</span>
            </div>""", unsafe_allow_html=True)

            st.info("📋 هذه المنتجات وجدها المحرك لدينا — تحقق بصرياً من دقة التطابق")

            by_brand: dict = defaultdict(list)
            for r in avail_filtered:
                by_brand[r.get("brand_group","أخرى")].append(r)

            for brand_name, products in sorted(by_brand.items(), key=lambda x: -len(x[1])):
                st.markdown(f'<div class="brand-hdr">🏷️ {brand_name} &nbsp;<span class="badge badge-cnt">{len(products)}</span></div>', unsafe_allow_html=True)

                show_all = st.checkbox(f"عرض الكل ({len(products)})", key=f"sa_avail_{brand_name}")
                products_show = products if show_all else products[:9]

                for idx in range(0, len(products_show), 3):
                    cols = st.columns(3)
                    for j, prod in enumerate(products_show[idx:idx+3]):
                        with cols[j]:
                            # Side-by-side image comparison
                            img_comp, img_ours = st.columns(2)
                            with img_comp:
                                cimg = prod.get("image","")
                                if cimg and cimg.startswith("http"):
                                    st.image(cimg, use_container_width=True)
                                else:
                                    st.markdown('<div style="height:100px;background:var(--surf);border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:.7rem;color:var(--muted);">المنافس</div>', unsafe_allow_html=True)
                                st.markdown('<div class="img-lbl">📦 المنافس</div>', unsafe_allow_html=True)
                            with img_ours:
                                oimg = prod.get("our_image","")
                                if oimg and oimg.startswith("http"):
                                    st.image(oimg, use_container_width=True)
                                else:
                                    st.markdown('<div style="height:100px;background:var(--surf);border-radius:6px;display:flex;align-items:center;justify-content:center;font-size:.7rem;color:var(--muted);">متجرنا</div>', unsafe_allow_html=True)
                                st.markdown('<div class="img-lbl">🌹 متجرنا</div>', unsafe_allow_html=True)

                            # Match info
                            st.markdown(f"""
                            <div style="font-size:.75rem;margin:.4rem 0;">
                              <div style="color:var(--muted);margin-bottom:2px;">المنافس:</div>
                              <div style="font-weight:600;font-size:.8rem;">{prod["name"][:60]}</div>
                              <div style="color:var(--muted);margin:.3rem 0 2px;">لدينا:</div>
                              <div style="font-weight:600;font-size:.8rem;color:var(--grn);">{prod.get("our_name","")[:60]}</div>
                              <div style="margin-top:.3rem;">
                                <span class="badge badge-gold">{prod["score"]:.0f}%</span>
                                <span class="badge badge-cnt" style="font-size:.65rem;">{prod["reason"]}</span>
                              </div>
                              <div style="display:flex;gap:8px;margin-top:.3rem;font-size:.8rem;">
                                <span>💰 منافس: {prod.get("price","")} ر.س</span>
                                <span style="color:var(--grn);">🌹 نحن: {prod.get("our_price","")} ر.س</span>
                              </div>
                            </div>""", unsafe_allow_html=True)
                            st.divider()

# ─── TAB 3: DESCRIPTION GENERATOR ─────────────────────

with tab3:
    if not st.session_state.engine_done:
        st.info("▶️ شغّل المحرك أولاً")
    elif not st.session_state.approved:
        st.warning("👁️ انتقل إلى **المراجعة البصرية** وافق على المنتجات التي تريد إضافتها أولاً")
    else:
        categories = load_categories(cats_file)
        brands_dict = load_brands(brands_file)
        not_avail_dedup = deduplicate_missing(st.session_state.not_avail)
        
        approved_products = [r for r in not_avail_dedup
                             if prod_key(r["name"],r["sz"]) in st.session_state.approved]

        st.markdown(f'<div class="sec-title">✍️ توليد أوصاف {len(approved_products)} منتج موافق عليه</div>',
                    unsafe_allow_html=True)

        # Bulk generate button
        b1, b2, _ = st.columns([2,2,4])
        with b1:
            if st.button("⚡ توليد جميع الأوصاف", type="primary", use_container_width=True):
                pbar = st.progress(0)
                for i, prod in enumerate(approved_products):
                    pkey = prod_key(prod["name"], prod["sz"])
                    if pkey not in st.session_state.descriptions:
                        prod_data = st.session_state.product_edits.get(pkey, {**prod})
                        prod_data.setdefault("category", suggest_category(prod["name"], categories))
                        prod_data.setdefault("brand", detect_brand_from_name(prod["name"], brands_dict))
                        prod_data.setdefault("concentration", extract_concentration(full_norm(prod["name"])))
                        desc = generate_description(prod_data)
                        st.session_state.descriptions[pkey] = desc
                    pbar.progress((i+1)/len(approved_products))
                st.success("✅ تم توليد جميع الأوصاف!")
        with b2:
            st.caption(f"⏱️ تقدير: ~{len(approved_products)*8} ثانية")

        st.divider()

        for prod in approved_products:
            pkey = prod_key(prod["name"], prod["sz"])
            edit_data = st.session_state.product_edits.get(pkey, {**prod})
            
            with st.expander(f"{'✅ ' if pkey in st.session_state.descriptions else '⏳ '}{prod['name'][:70]}", expanded=False):
                col_img, col_info = st.columns([1, 3])
                with col_img:
                    img = prod.get("image","")
                    if img and img.startswith("http"):
                        st.image(img, use_container_width=True)
                    st.markdown(f"**السعر:** {prod.get('min_price','')} ر.س")
                    st.markdown(f"**المنافسون:** {prod.get('competitor_count',1)}")

                with col_info:
                    r1, r2 = st.columns(2)
                    with r1:
                        new_name  = st.text_input("اسم المنتج", value=edit_data.get("name", prod["name"]), key=f"name_{pkey}")
                        new_price = st.text_input("السعر (ر.س)", value=edit_data.get("price", prod.get("min_price","")), key=f"price_{pkey}")
                        new_brand = st.text_input("الماركة", value=edit_data.get("brand", detect_brand_from_name(prod["name"], brands_dict)), key=f"brand_{pkey}")
                    with r2:
                        cat_options = [""] + categories
                        default_cat = edit_data.get("category", suggest_category(prod["name"], categories))
                        cat_idx = cat_options.index(default_cat) if default_cat in cat_options else 0
                        new_cat   = st.selectbox("التصنيف", cat_options, index=cat_idx, key=f"cat_{pkey}")
                        new_gender= st.selectbox("الجنس", ["للجنسين","نسائي","رجالي"],
                                                  index=["للجنسين","نسائي","رجالي"].index(edit_data.get("gender","للجنسين")) if edit_data.get("gender") in ["للجنسين","نسائي","رجالي"] else 0,
                                                  key=f"gender_{pkey}")

                    # Update edit data
                    st.session_state.product_edits[pkey] = {
                        **edit_data,
                        "name": new_name, "price": new_price,
                        "brand": new_brand, "category": new_cat,
                        "gender": new_gender,
                    }

                    # Description area
                    if pkey in st.session_state.descriptions:
                        st.markdown("**الوصف المُولَّد:**")
                        edited_desc = st.text_area("تعديل الوصف", value=st.session_state.descriptions[pkey],
                                                    height=200, key=f"desc_{pkey}")
                        st.session_state.descriptions[pkey] = edited_desc
                        st.markdown("**معاينة:**")
                        st.markdown(f'<div class="desc-box">{edited_desc}</div>', unsafe_allow_html=True)
                    else:
                        if st.button(f"⚡ توليد الوصف", key=f"gen_{pkey}", use_container_width=True, type="primary"):
                            with st.spinner("جارٍ التوليد..."):
                                d = generate_description(st.session_state.product_edits.get(pkey, prod))
                                st.session_state.descriptions[pkey] = d
                            st.rerun()

# ─── TAB 4: EXPORT ───────────────────────────────────

with tab4:
    if not st.session_state.engine_done:
        st.info("▶️ شغّل المحرك أولاً")
    else:
        not_avail_dedup = deduplicate_missing(st.session_state.not_avail)
        approved_products = [r for r in not_avail_dedup
                             if prod_key(r["name"],r["sz"]) in st.session_state.approved]

        # Determine readiness
        has_desc    = [p for p in approved_products if prod_key(p["name"],p["sz"]) in st.session_state.descriptions]
        no_desc     = [p for p in approved_products if prod_key(p["name"],p["sz"]) not in st.session_state.descriptions]

        st.markdown('<div class="sec-title">📤 التصدير</div>', unsafe_allow_html=True)

        m = st.columns(3)
        with m[0]:
            st.markdown(f'<div class="metric-card"><div class="metric-val">{len(approved_products)}</div><div class="metric-lbl">👍 منتج موافق عليه</div></div>', unsafe_allow_html=True)
        with m[1]:
            st.markdown(f'<div class="metric-card"><div class="metric-val">{len(has_desc)}</div><div class="metric-lbl">✍️ جاهز بوصف</div></div>', unsafe_allow_html=True)
        with m[2]:
            st.markdown(f'<div class="metric-card"><div class="metric-val">{len(no_desc)}</div><div class="metric-lbl">⏳ بدون وصف بعد</div></div>', unsafe_allow_html=True)

        st.divider()

        if not approved_products:
            st.warning("لم توافق على أي منتج بعد — انتقل إلى تبويب المراجعة البصرية")
        else:
            exp1, exp2 = st.columns(2)
            
            with exp1:
                st.subheader("📦 تصدير كل المنتجات الموافق عليها")
                st.caption("يشمل المنتجات بوصف وبدون وصف")
                if st.button("⬇️ تنزيل منتج_جديد.csv", use_container_width=True, type="primary"):
                    rows = []
                    for prod in approved_products:
                        pkey = prod_key(prod["name"], prod["sz"])
                        edit = st.session_state.product_edits.get(pkey, prod)
                        row = build_export_row({
                            "name":        edit.get("name", prod["name"]),
                            "category":    edit.get("category",""),
                            "image":       prod.get("image",""),
                            "price":       edit.get("price", prod.get("min_price","")),
                            "sz":          prod.get("sz",""),
                            "brand":       edit.get("brand",""),
                            "description": st.session_state.descriptions.get(pkey,""),
                        })
                        rows.append(row)
                    csv_bytes = to_csv_bytes(rows)
                    st.download_button("💾 حفظ الملف", data=csv_bytes,
                                       file_name="منتج_جديد.csv", mime="text/csv",
                                       use_container_width=True)

            with exp2:
                st.subheader("✍️ تصدير المنتجات بأوصاف فقط")
                st.caption("فقط المنتجات التي تم توليد وصفها")
                if has_desc and st.button("⬇️ تنزيل منتج_جديد_مع_أوصاف.csv", use_container_width=True):
                    rows = []
                    for prod in has_desc:
                        pkey = prod_key(prod["name"], prod["sz"])
                        edit = st.session_state.product_edits.get(pkey, prod)
                        row = build_export_row({
                            "name":        edit.get("name", prod["name"]),
                            "category":    edit.get("category",""),
                            "image":       prod.get("image",""),
                            "price":       edit.get("price", prod.get("min_price","")),
                            "sz":          prod.get("sz",""),
                            "brand":       edit.get("brand",""),
                            "description": st.session_state.descriptions.get(pkey,""),
                        })
                        rows.append(row)
                    csv_bytes = to_csv_bytes(rows)
                    st.download_button("💾 حفظ الملف", data=csv_bytes,
                                       file_name="منتج_جديد_مع_أوصاف.csv", mime="text/csv",
                                       use_container_width=True)

            st.divider()
            st.subheader("📋 معاينة المنتجات الجاهزة للتصدير")
            preview_data = []
            for prod in approved_products:
                pkey = prod_key(prod["name"], prod["sz"])
                edit = st.session_state.product_edits.get(pkey, prod)
                preview_data.append({
                    "اسم المنتج":      edit.get("name", prod["name"])[:50],
                    "التصنيف":         edit.get("category","")[:40],
                    "الماركة":         edit.get("brand","")[:30],
                    "السعر":           edit.get("price", prod.get("min_price","")),
                    "الحجم (مل)":     prod.get("sz",""),
                    "وصف جاهز":       "✅" if pkey in st.session_state.descriptions else "❌",
                    "عدد المنافسين":   prod.get("competitor_count",1),
                })
            st.dataframe(pd.DataFrame(preview_data), hide_index=True, use_container_width=True)
