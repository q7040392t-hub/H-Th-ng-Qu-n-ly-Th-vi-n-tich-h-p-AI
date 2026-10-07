import html
import math
from pathlib import Path

import pandas as pd
import streamlit as st

import auth
import database as db
from ai_service import AIService

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / 'static'
LOBBY_HERO = 'assets/lobby_tech.jpg'
LOBBY_DETECTIVE = 'assets/lobby_detective.jpg'
LOBBY_PHILOSOPHY = 'assets/lobby_philosophy.jpg'

st.set_page_config(
    page_title='SmartLibrary AI',
    page_icon='📚',
    layout='wide',
    initial_sidebar_state='expanded',
)

@st.cache_resource(show_spinner=False)
def _bootstrap_app():
    db.init_db()
    db.seed_books()
    auth.ensure_demo_accounts()
    db.seed_demo_workflows()
    db.refresh_overdue(force=True)
    return True

_bootstrap_app()

if 'ui_theme' not in st.session_state:
    st.session_state.ui_theme='light'

# ------------------------------------------------------------------
# STYLE
# ------------------------------------------------------------------
st.markdown(r'''
<style>
:root{
  --p1:#655cf6;--p2:#8b5cf6;--pink:#e544ba;--ink:#111827;--muted:#64748b;
  --line:#e7eaf2;--soft:#f6f7ff;--soft2:#fbf7ff;--green:#21b887;--red:#ff5964;
}
html,body,[class*="css"]{font-family:Inter,Segoe UI,Arial,sans-serif;}
.stApp{background:linear-gradient(135deg,#f7f9ff 0%,#f8f6ff 42%,#fff8fd 100%);color:var(--ink);}
.block-container{max-width:1540px;padding-top:1rem;padding-bottom:3rem;}
header[data-testid="stHeader"]{display:none!important;height:0!important;min-height:0!important;}
[data-testid="stToolbar"], [data-testid="stStatusWidget"], [data-testid="stDecoration"], #MainMenu{display:none!important;}
footer{visibility:hidden;}

/* General widgets */
.stButton>button{border-radius:12px;border:1px solid #e1def7;background:#fff;color:#3f3d68;font-weight:750;min-height:42px;}
.stButton>button:hover{border-color:#8b5cf6;color:#655cf6;background:#f8f6ff;}
.stButton>button[kind="primary"]{border:0;background:linear-gradient(100deg,#655cf6,#a64ee7,#e544ba);color:#fff;box-shadow:0 9px 22px rgba(122,89,239,.20);}
input,textarea{border-radius:12px!important;}
[data-testid="stMetric"]{background:white;border:1px solid var(--line);border-radius:18px;padding:13px 16px;box-shadow:0 8px 20px rgba(53,55,111,.05);}

/* Public lobby */
.public-shell{max-width:1420px;margin:0 auto;}
.public-nav{background:rgba(255,255,255,.93);border:1px solid rgba(224,226,238,.9);border-radius:22px;padding:13px 22px;box-shadow:0 12px 32px rgba(72,65,130,.06);margin-bottom:16px;}
.brand{display:flex;align-items:center;gap:11px;font-size:1.45rem;font-weight:950;color:#111827;line-height:1;}
.brand-icon{display:inline-flex;width:44px;height:44px;border-radius:14px;background:linear-gradient(135deg,#665cf6,#a64ee7,#ed47b1);align-items:center;justify-content:center;color:#fff;font-size:1.35rem;box-shadow:0 9px 20px rgba(122,89,239,.18);}
.ai-badge{font-size:.66rem;background:linear-gradient(135deg,#8b5cf6,#e544ba);color:white;padding:3px 7px;border-radius:7px;margin-left:4px;vertical-align:middle;}
.hero-public{background:linear-gradient(120deg,#f5f7ff,#f5f1ff 50%,#f9effb);border:1px solid #e8e9f6;border-radius:30px;overflow:hidden;box-shadow:0 18px 45px rgba(86,78,150,.08);padding:44px 48px;display:grid;grid-template-columns:1.05fr 1fr;gap:35px;align-items:center;min-height:450px;}
.hero-kicker{color:#625ad9;font-weight:900;font-size:1rem;margin-bottom:12px;}
.hero-title{font-size:3rem;line-height:1.07;font-weight:950;color:#172033;margin:0 0 16px;letter-spacing:-1.5px;}
.hero-title span{background:linear-gradient(90deg,#655cf6,#b347de,#e544ba);-webkit-background-clip:text;color:transparent;}
.hero-desc{font-size:1.06rem;line-height:1.75;color:#657087;max-width:650px;}
.hero-image{border-radius:25px;overflow:hidden;box-shadow:0 18px 45px rgba(66,57,123,.17);height:340px;background-size:cover;background-position:center;position:relative;}
.hero-image:after{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(110,92,246,.13),rgba(236,72,153,.08));}
.public-section-title{text-align:center;font-size:1.65rem;font-weight:950;color:#20283a;margin:34px 0 7px;}
.public-section-sub{text-align:center;color:#8590a3;margin-bottom:20px;}
.stat-card{background:#fff;border:1px solid #e8eaf2;border-radius:19px;padding:18px;text-align:center;box-shadow:0 10px 24px rgba(48,54,94,.05);}
.stat-icon{font-size:1.45rem}.stat-num{font-size:1.55rem;font-weight:950;color:#514ad5;margin-top:5px}.stat-label{font-size:.8rem;color:#8992a4;font-weight:700;}
.cat-card{background:#fff;border:1px solid #e8eaf2;border-radius:19px;padding:18px;min-height:120px;text-align:center;box-shadow:0 10px 24px rgba(48,54,94,.04);}
.cat-icon{width:48px;height:48px;border-radius:14px;display:flex;align-items:center;justify-content:center;margin:0 auto 10px;font-size:1.35rem;background:linear-gradient(135deg,#edeaff,#ffe9f6);}
.cat-title{font-weight:900;color:#2d3548;font-size:.92rem}.cat-count{font-size:.75rem;color:#98a0ae;margin-top:4px;}
.book-tile{background:#fff;border:1px solid #e7e9f1;border-radius:18px;padding:12px;box-shadow:0 8px 20px rgba(57,54,99,.045);min-height:330px;}
.book-name{font-size:.92rem;font-weight:900;color:#283044;line-height:1.35;margin-top:8px;}.book-meta{font-size:.76rem;color:#8790a1;line-height:1.55;margin-top:4px;}.badge{display:inline-block;margin-top:6px;padding:4px 8px;border-radius:999px;background:#f1ecff;color:#7555cb;font-size:.68rem;font-weight:850;}
.public-footer{background:#161722;color:#cbd0dc;border-radius:26px 26px 0 0;padding:32px;margin-top:42px;}.public-footer b{color:white}.footer-head{font-size:1.15rem;font-weight:950;color:#fff;margin-bottom:8px;}.footer-small{font-size:.82rem;line-height:1.8;color:#aeb5c5;}

/* Login */
.login-wrap{max-width:620px;margin:5vh auto 0;}
.login-card{background:rgba(255,255,255,.96);border:1px solid #e6e7ef;border-radius:26px;padding:28px 34px;box-shadow:0 25px 65px rgba(50,53,95,.20);}
.login-brand{text-align:center;margin-bottom:20px;}.login-logo{width:58px;height:58px;border-radius:17px;margin:0 auto 13px;display:flex;align-items:center;justify-content:center;background:linear-gradient(135deg,#655cf6,#9c51e9,#e544ba);color:#fff;font-size:1.7rem;font-weight:950;box-shadow:0 10px 25px rgba(113,82,229,.24);}
.login-title{font-size:1.75rem;font-weight:950;color:#111827}.login-sub{color:#657087;margin-top:4px}.quick-title{text-align:center;color:#657087;font-size:.9rem;margin:16px 0 10px;}

/* Sidebar logged-in */
[data-testid="stSidebar"]{background:#fff;border-right:1px solid #e9eaf1;}
[data-testid="stSidebar"] .block-container{padding-top:1.15rem!important;}
.side-brand{display:flex;gap:12px;align-items:center;padding:4px 3px 15px;}.side-title{font-size:1.22rem;font-weight:950;color:#121827;}.side-sub{font-size:.78rem;color:#748095;margin-top:2px;}.profile-card{border:1px solid #e8e9ef;border-radius:17px;padding:13px;background:#fff;margin:5px 0 13px;}.role-chip{display:inline-block;border-radius:999px;padding:4px 8px;background:#ffe9ef;color:#f04464;font-size:.66rem;font-weight:900;}.profile-name{font-size:.91rem;font-weight:900;color:#1d2433;margin-top:5px;}
[data-testid="stSidebar"] div[role="radiogroup"] label{border-radius:12px;padding:8px 9px;margin:2px 0;transition:.15s;}
[data-testid="stSidebar"] div[role="radiogroup"] label:hover{background:#f6f5ff;}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked){background:linear-gradient(90deg,#655cf6,#7168f2);color:white!important;}
[data-testid="stSidebar"] div[role="radiogroup"] label:has(input:checked) *{color:white!important;}
.side-group{font-size:.7rem;color:#a4abc0;font-weight:900;letter-spacing:1.3px;margin:14px 4px 4px;}

/* App pages */
.page-title{font-size:1.7rem;font-weight:950;color:#161d2d;margin:4px 0 2px;}.page-sub{color:#8992a3;margin-bottom:16px;font-size:.91rem;}.panel{background:#fff;border:1px solid #e7e9f1;border-radius:19px;padding:17px;box-shadow:0 8px 22px rgba(46,50,91,.04);}.mini-title{font-weight:900;color:#283044;font-size:1rem;margin-bottom:10px;}.metric-card{background:#fff;border:1px solid #e7e9f1;border-radius:18px;padding:16px;box-shadow:0 8px 22px rgba(46,50,91,.04);}.metric-label{font-size:.76rem;color:#8a93a5;font-weight:750}.metric-value{font-size:1.6rem;color:#5e57e3;font-weight:950;margin-top:4px}.small-muted{font-size:.75rem;color:#9099aa}.status-ok{color:#10a870;font-weight:800}.status-bad{color:#eb4d61;font-weight:800}

@media(max-width:900px){.hero-public{grid-template-columns:1fr;padding:28px}.hero-title{font-size:2.3rem}.hero-image{height:260px}.block-container{padding-left:.7rem;padding-right:.7rem;}}

/* ===== PUBLIC LOBBY V5: LIBRA pink-purple ===== */
.public-shell{max-width:100%;margin:0;}
.public-nav{background:#fff;border:0;border-radius:0;padding:0 3.8%;box-shadow:0 3px 18px rgba(77,45,120,.06);margin:0;}
.public-top-strip{margin:0;min-height:58px;display:flex;align-items:center;justify-content:center;background:linear-gradient(100deg,#7939f5 0%,#c629d0 48%,#ef3b91 100%);color:white;font-weight:950;letter-spacing:.35px;font-size:1.03rem;}
.public-logo{color:#8a39e8;font-size:2rem;font-weight:1000;letter-spacing:2px;white-space:nowrap;padding-top:9px;}
.public-logo small{font-size:.62rem;color:#9a45ef;margin-left:6px;}
.public-nav [data-testid="stButton"] button{border:0!important;background:transparent!important;box-shadow:none!important;min-height:54px!important;color:#493758!important;font-weight:850!important;padding:.35rem .25rem!important;}
.public-nav [data-testid="stButton"] button:hover{color:#9a3ee4!important;background:#fbf7ff!important;}
.nav-action [data-testid="stButton"] button{border:1px solid #eadcf9!important;border-radius:999px!important;min-height:48px!important;padding:.4rem .8rem!important;}
.nav-login [data-testid="stButton"] button{border:0!important;border-radius:999px!important;color:white!important;background:linear-gradient(100deg,#8b4cf6,#e43fa8)!important;box-shadow:0 8px 20px rgba(184,65,204,.18)!important;}
.hero-carousel{position:relative;height:650px;overflow:hidden;background:#442067;}
.hero-slide{position:absolute;inset:0;background-size:cover;background-position:center;opacity:0;animation:libraHero 18s infinite;}
.hero-slide.s1{animation-delay:0s}.hero-slide.s2{animation-delay:6s}.hero-slide.s3{animation-delay:12s}
.hero-slide:before{content:"";position:absolute;inset:0;background:linear-gradient(90deg,rgba(82,36,125,.82) 0%,rgba(141,63,185,.54) 46%,rgba(235,89,151,.20) 100%);}
.hero-slide:after{content:"";position:absolute;left:0;right:0;bottom:0;height:145px;background:linear-gradient(transparent,rgba(255,248,254,.96));}
@keyframes libraHero{0%{opacity:0}4%{opacity:1}29%{opacity:1}34%{opacity:0}100%{opacity:0}}
.hero-copy{position:absolute;z-index:3;left:6%;top:31%;max-width:690px;color:#fff;}
.hero-chip{display:inline-flex;padding:9px 15px;border-radius:999px;border:1px solid rgba(255,255,255,.35);background:rgba(255,255,255,.17);font-size:.86rem;font-weight:900;backdrop-filter:blur(6px);margin-bottom:15px;}
.hero-copy h1{margin:0 0 17px;font-size:3.35rem;line-height:1.08;font-weight:1000;letter-spacing:-1.5px;color:#fff;max-width:700px;}
.hero-copy p{margin:0;font-size:1.05rem;line-height:1.7;color:#fff;max-width:670px;font-weight:550;text-shadow:0 2px 12px rgba(50,20,70,.12);}
.hero-search-panel{max-width:1080px;margin:-38px auto 16px;position:relative;z-index:20;background:#fff;border:1px solid #eadff5;border-radius:20px;padding:14px 18px;box-shadow:0 15px 38px rgba(95,50,130,.13);}
.public-content-pad{padding:0 4%;}
.public-section-title{color:#3d2852;}
.stat-card,.cat-card,.book-tile{border-color:#eadff3;box-shadow:0 9px 24px rgba(111,61,149,.06);}
.stat-num{color:#933ee6;}.cat-icon{background:linear-gradient(135deg,#efe7ff,#ffe4f2);}.badge{background:#f6e9ff;color:#8e39d2;}
.public-footer{background:#21152c;color:#d9cce3;border-radius:0;padding:38px 5%;margin-top:45px;}
.footer-grid{display:grid;grid-template-columns:1.4fr 1fr 1fr 1fr;gap:32px;}.footer-brand{font-size:2rem;font-weight:1000;color:#d45be8;letter-spacing:1.5px;}.footer-head{font-size:1rem;font-weight:950;color:#fff;margin-bottom:11px;}.footer-small{font-size:.82rem;line-height:1.85;color:#c5b7ce;}.footer-link{font-size:.82rem;line-height:2;color:#c5b7ce;}
.floating-ai{position:fixed;right:34px;bottom:28px;width:70px;height:70px;border-radius:50%;display:flex;align-items:center;justify-content:center;z-index:9999;background:linear-gradient(135deg,#8a3ff1,#e33dac);color:#fff!important;font-size:1.8rem;text-decoration:none!important;box-shadow:0 14px 35px rgba(156,55,202,.32);border:1px solid rgba(255,255,255,.45);}.floating-ai:hover{transform:translateY(-2px);filter:brightness(1.05);}
.login-page-wrap{max-width:560px;margin:5vh auto 7vh;}.login-mode-title{text-align:center;color:#22283a;font-size:2rem;font-weight:1000;margin:8px 0 4px;}.login-mode-sub{text-align:center;color:#7e8797;margin-bottom:18px;}
@media(max-width:1000px){.hero-carousel{height:560px}.hero-copy{left:5%;top:26%;max-width:600px}.hero-copy h1{font-size:2.7rem}.footer-grid{grid-template-columns:1fr 1fr}}
@media(max-width:700px){.hero-carousel{height:520px}.hero-copy{top:24%;right:5%}.hero-copy h1{font-size:2.25rem}.footer-grid{grid-template-columns:1fr}.public-top-strip{font-size:.82rem}}

/* ===== V7 FINAL VISUAL FIXES ===== */
.book-tile{
    min-height:0!important;
    padding:10px!important;
    border-radius:16px!important;
    overflow:hidden!important;
}
.book-cover-img{
    display:block!important;
    width:100%!important;
    height:255px!important;
    object-fit:cover!important;
    object-position:center top!important;
    border-radius:12px!important;
    background:#f7f0fb!important;
}
.book-cover-empty{
    width:100%;height:255px;border-radius:12px;
    display:flex;align-items:center;justify-content:center;
    background:linear-gradient(135deg,#f2eaff,#ffe9f5);font-size:2.2rem;
}
.book-name{font-size:.88rem!important;line-height:1.35!important;margin-top:9px!important;min-height:2.4em!important;}
.book-meta{font-size:.72rem!important;line-height:1.45!important;}

.floating-ai{
    right:24px!important;bottom:22px!important;
    width:52px!important;height:52px!important;
    min-width:52px!important;min-height:52px!important;
    padding:0!important;font-size:0!important;border-radius:50%!important;
    background:linear-gradient(135deg,#8b3df2 0%,#d73ec7 57%,#ee429e 100%)!important;
    box-shadow:0 9px 24px rgba(151,47,196,.28)!important;
    border:1px solid rgba(255,255,255,.7)!important;
}
.chat-glyph{position:relative;display:block;width:24px;height:17px;border-radius:50%;background:#fff;box-shadow:inset 0 -3px 7px rgba(118,74,155,.13);}
.chat-glyph:after{content:"";position:absolute;right:2px;bottom:-4px;width:8px;height:8px;background:#fff;clip-path:polygon(0 0,100% 0,100% 100%);transform:rotate(18deg);}

/* Separate home after login */
.staff-home-hero{
    border-radius:20px;padding:22px 24px;margin-bottom:18px;
    background:linear-gradient(105deg,#ffffff 0%,#faf7ff 62%,#fff0f8 100%);
    border:1px solid #e8e3f3;box-shadow:0 10px 30px rgba(79,57,128,.06);
}
.staff-home-kicker{font-size:.8rem;color:#8e98aa;font-weight:800;letter-spacing:.4px;}
.staff-home-title{font-size:1.85rem;color:#20283a;font-weight:1000;margin-top:5px;}
.staff-home-sub{font-size:.91rem;color:#7d8798;margin-top:4px;}
.quick-card{
    border-radius:18px;padding:18px 18px 15px;min-height:132px;color:#fff;
    box-shadow:0 12px 27px rgba(73,64,145,.14);margin-bottom:6px;
}
.quick-card.q1{background:linear-gradient(135deg,#615cf1,#8077f7);}
.quick-card.q2{background:linear-gradient(135deg,#8a49e3,#b95adc);}
.quick-card.q3{background:linear-gradient(135deg,#e34a9a,#ee6f92);}
.quick-card.q4{background:linear-gradient(135deg,#476ac4,#5f8adf);}
.quick-card.q5{background:linear-gradient(135deg,#00b894,#00cec9);}
.quick-card.q6{background:linear-gradient(135deg,#f59e0b,#d97706);}
.quick-icon{font-size:1.65rem;margin-bottom:10px;}.quick-name{font-size:1rem;font-weight:950;}.quick-desc{font-size:.74rem;line-height:1.45;color:rgba(255,255,255,.86);margin-top:5px;}
.home-metric{background:#fff;border:1px solid #e7e9f2;border-radius:18px;padding:16px 17px;box-shadow:0 8px 22px rgba(46,50,91,.045);}
.home-metric-label{font-size:.76rem;color:#8b94a6;font-weight:800}.home-metric-value{font-size:1.65rem;color:#5650dc;font-weight:1000;margin-top:5px}.home-metric-note{font-size:.68rem;color:#a0a7b5;margin-top:3px}
.home-panel{background:#fff;border:1px solid #e7e9f2;border-radius:19px;padding:18px;box-shadow:0 8px 22px rgba(46,50,91,.045);}
.home-panel-title{font-size:.98rem;font-weight:950;color:#2b3346;margin-bottom:12px;}
.activity-row{padding:9px 0;border-bottom:1px solid #f0f1f6;}.activity-row:last-child{border-bottom:0}.activity-title{font-size:.82rem;font-weight:850;color:#374055}.activity-detail{font-size:.7rem;color:#939cad;margin-top:2px}
[data-testid="stSidebar"] .stButton>button{justify-content:flex-start!important;text-align:left!important;}

/* ===== V10 READER MEMBER PORTAL - LIGHT ===== */
.reader-portal .stApp{background:linear-gradient(135deg,#f8f9ff,#fff8fd)!important;color:#20253a!important;}
.reader-dark-page{background:transparent;color:#20253a;min-height:100vh;}
.reader-top-card{background:linear-gradient(135deg,#ffffff 0%,#faf6ff 55%,#fff2f8 100%);border:1px solid #eadff5;border-radius:22px;padding:22px;margin-bottom:18px;box-shadow:0 12px 30px rgba(93,61,143,.08);}
.reader-welcome{font-size:1.8rem;font-weight:1000;color:#20233d;margin:0 0 5px}.reader-muted{color:#7c8498;font-size:.88rem;}
.reader-chip{display:inline-block;border-radius:999px;padding:5px 11px;background:#f1e8ff;color:#7a43cf;font-size:.72rem;font-weight:950;margin-right:6px;}
.reader-stat{background:#fff;border:1px solid #e8e5f3;border-radius:18px;padding:17px;min-height:96px;box-shadow:0 8px 22px rgba(72,54,120,.05);}.reader-stat-label{font-size:.75rem;color:#81899d;font-weight:800}.reader-stat-value{font-size:1.55rem;font-weight:1000;color:#7a4ce6;margin-top:5px}
.reader-panel{background:#fff;border:1px solid #e7e5f1;border-radius:19px;padding:19px;margin-bottom:17px;box-shadow:0 8px 22px rgba(72,54,120,.045);}.reader-panel h3{color:#272b42!important;margin-top:0}.reader-panel-title{font-size:1.07rem;font-weight:1000;color:#292d45;margin-bottom:12px;}
.reader-tabbar{display:flex;gap:8px;flex-wrap:wrap;margin:5px 0 18px}.reader-tab{padding:9px 14px;border-radius:11px;border:1px solid #e2ddf0;color:#655575;background:#fff;font-size:.82rem;font-weight:850}.reader-tab.active{background:linear-gradient(90deg,#705cf2,#d944b6);color:white;border-color:transparent;}
.reader-empty{text-align:center;padding:65px 15px;color:#7f8798}.reader-empty-icon{font-size:3rem;color:#9d78eb;margin-bottom:12px}.reader-empty-title{font-weight:950;color:#292d45;font-size:1.05rem}.reader-empty-sub{color:#8990a0;font-size:.87rem;margin-top:6px}
.reader-profile-box{background:#fff;border:1px solid #e5e1ef;border-radius:17px;padding:18px;box-shadow:0 7px 20px rgba(72,54,120,.04)}.reader-avatar{width:82px;height:82px;border-radius:50%;background:linear-gradient(135deg,#8a5cf6,#eb43a8);border:3px solid #f3d7ff;display:flex;align-items:center;justify-content:center;font-size:2.2rem;margin:auto;color:#fff}.reader-name{font-size:1.2rem;font-weight:1000;color:#252940}.reader-expiry{font-size:.8rem;color:#868da0}.reader-points{font-size:.82rem;color:#8a4fe6;margin-top:8px;font-weight:850}.reader-badge{background:linear-gradient(90deg,#725cf2,#d842b7);color:#fff;padding:8px 14px;border-radius:999px;font-weight:900;display:inline-block;margin-top:10px}
.reader-book-card{background:#fff;border:1px solid #e7e4ef;border-radius:15px;padding:10px;min-height:330px;box-shadow:0 8px 22px rgba(72,54,120,.045)}.reader-book-cover{width:100%;height:235px;object-fit:cover;border-radius:11px;background:#f3eff8}.reader-book-title{font-weight:950;color:#2b3046;font-size:.86rem;line-height:1.35;margin-top:8px}.reader-book-meta{font-size:.7rem;color:#878e9f;margin-top:4px}
.reader-history-row{display:grid;grid-template-columns:1.2fr 2.5fr 1fr 1fr;gap:12px;padding:12px 0;border-bottom:1px solid #efedf4;align-items:center;font-size:.82rem;color:#3e4458}.reader-history-row:last-child{border-bottom:0}.reader-status{color:#7a4ce6;font-weight:900}
.reader-achievement{background:linear-gradient(145deg,#ffffff,#fbf8ff);border:1px solid #e7e3ef;border-radius:17px;padding:16px;text-align:center;box-shadow:0 7px 20px rgba(72,54,120,.04)}.reader-ach-icon{font-size:2rem}.reader-ach-title{font-weight:950;color:#2a2e45;margin-top:7px}.reader-ach-desc{font-size:.72rem;color:#858c9d;margin-top:4px}
.reader-support-item{padding:13px;border:1px solid #e7e3ee;border-radius:14px;background:#fff;margin-bottom:10px}.reader-support-title{font-weight:950;color:#292e45}.reader-support-meta{font-size:.72rem;color:#858c9d;margin-top:4px}
.reader-security-card{border:1px solid #e6e2ef;border-radius:14px;padding:14px;background:#fff;color:#2b3047;margin-bottom:10px}

body:has(.reader-theme-marker) [data-testid="stSidebar"]{background:#fff!important;border-right:1px solid #ebe7f3!important;}
body:has(.reader-theme-marker) [data-testid="stSidebar"] *{color:#34384d!important;}
body:has(.reader-theme-marker) [data-testid="stSidebar"] .side-title{color:#20243a!important;}
body:has(.reader-theme-marker) [data-testid="stSidebar"] .side-sub{color:#8a91a2!important;}
body:has(.reader-theme-marker) [data-testid="stSidebar"] .profile-card{background:#fff!important;border:1px solid #e9e5f1!important;}
body:has(.reader-theme-marker) [data-testid="stSidebar"] .stButton>button{background:#fff!important;border:1px solid transparent!important;color:#3d4257!important;justify-content:flex-start!important;text-align:left!important;min-height:47px!important;border-radius:13px!important;font-weight:850!important;padding-left:14px!important;}
body:has(.reader-theme-marker) [data-testid="stSidebar"] .stButton>button:hover{background:#f8f4ff!important;color:#7b46dc!important;border-color:#eadff8!important;}
body:has(.reader-theme-marker) [data-testid="stSidebar"] .stButton>button[kind="primary"]{background:linear-gradient(90deg,#6d5cf2,#a44de7,#df43b4)!important;color:#fff!important;border:0!important;box-shadow:0 8px 20px rgba(122,74,224,.18)!important;}
body:has(.reader-theme-marker) [data-testid="stSidebar"] .stButton>button[kind="primary"] *{color:#fff!important;}
body:has(.reader-theme-marker) [data-testid="stSidebar"] hr{border-color:#ece8f3!important;}
body:has(.reader-theme-marker) .stApp{background:linear-gradient(135deg,#f8f9ff 0%,#fbf8ff 45%,#fff8fc 100%)!important;color:#262a40!important;}
body:has(.reader-theme-marker) header[data-testid="stHeader"]{background:rgba(255,255,255,.92)!important;}
body:has(.reader-theme-marker) [data-testid="stTextInput"] input,body:has(.reader-theme-marker) [data-testid="stTextArea"] textarea,body:has(.reader-theme-marker) [data-testid="stSelectbox"] div[data-baseweb="select"]>div{background:#fff!important;color:#2f3448!important;border-color:#e1ddeb!important;}
body:has(.reader-theme-marker) [data-testid="stButton"] button{background:#fff;color:#464b60;border-color:#e3dff0;font-weight:800;}
body:has(.reader-theme-marker) [data-testid="stButton"] button[kind="primary"]{background:linear-gradient(90deg,#6e5cf2,#df43b3)!important;color:#fff!important;border:0!important;}

body:not(:has(.reader-theme-marker)) [data-testid="stSidebar"] .stButton>button{font-weight:900!important;border-radius:13px!important;border:1px solid #ece8f7!important;background:#fff!important;min-height:48px!important;padding-left:13px!important;}
body:not(:has(.reader-theme-marker)) [data-testid="stSidebar"] .stButton>button:hover{background:#faf7ff!important;border-color:#d9cdf6!important;color:#7048d8!important;}
body:not(:has(.reader-theme-marker)) [data-testid="stSidebar"] .stButton>button[kind="primary"]{background:linear-gradient(90deg,#655cf6,#9153ea,#dc43b7)!important;color:#fff!important;border:0!important;box-shadow:0 8px 20px rgba(112,76,221,.18)!important;}
body:not(:has(.reader-theme-marker)) [data-testid="stSidebar"] .stButton>button[kind="primary"] *{color:#fff!important;}
body:not(:has(.reader-theme-marker)) [data-testid="stSidebar"] .side-group{color:#8b68d1!important;font-weight:1000!important;letter-spacing:1.5px!important;}

.login-page-wrap{max-width:560px!important;margin:3vh auto 5vh!important;}.login-mode-title{font-size:1.55rem!important;margin-top:2px!important;}.login-mode-sub{font-size:.86rem!important;margin-bottom:12px!important;}

div[role="dialog"]{background:#111315!important;color:#f7f7f8!important;border:1px solid #2a2d30!important;border-radius:22px!important;box-shadow:0 25px 70px rgba(0,0,0,.38)!important;}
div[role="dialog"] [data-testid="stMarkdownContainer"] p,div[role="dialog"] [data-testid="stMarkdownContainer"] li,div[role="dialog"] label{color:#f4f4f5!important;}
div[role="dialog"] [data-testid="stButton"] button{background:#2a2c2f!important;color:#fff!important;border:1px solid #34373a!important;border-radius:13px!important;font-weight:850!important;min-height:50px!important;}
div[role="dialog"] [data-testid="stButton"] button:hover{background:#333639!important;border-color:#16c99a!important;}
div[role="dialog"] input{background:#191b1e!important;color:#fff!important;border-color:#34373a!important;}
.chat-popup-head{margin:-1rem -1rem 16px -1rem;padding:14px 17px;background:linear-gradient(90deg,#12b98d,#18c9a0);border-radius:20px 20px 0 0;color:#fff;font-size:1.15rem;font-weight:1000;}
.chat-popup-bot{width:72px;height:72px;border-radius:50%;background:linear-gradient(135deg,#77f2d3,#13b68c);display:flex;align-items:center;justify-content:center;margin:8px auto 8px;font-size:2.2rem;border:3px solid #99ffe5;box-shadow:0 8px 22px rgba(16,185,141,.22);}
.chat-popup-title{text-align:center;color:#fff;font-size:1.6rem;font-weight:1000;margin:4px 0 2px;}.chat-popup-sub{text-align:center;color:#d2d4d7;font-size:.86rem;margin-bottom:14px;}


/* ===== V12 PERFORMANCE / UI FINISH ===== */
.floating-ai{
    width:44px!important;height:44px!important;min-width:44px!important;min-height:44px!important;
    right:16px!important;bottom:16px!important;
    box-shadow:0 7px 18px rgba(151,55,197,.25)!important;
}
.chat-glyph{width:21px!important;height:15px!important;}
.book-cover-img{content-visibility:auto;}
.hero-slide{will-change:opacity;}
.stApp{scroll-behavior:smooth;}
/* Less expensive shadows on large repeated card grids */
.book-tile,.reader-book-card,.stat-card,.cat-card{box-shadow:0 5px 14px rgba(70,55,110,.045)!important;}

/* ===== V14 FAST AI + POLISHED ADMIN ===== */
.admin-summary-card{background:#fff;border:1px solid #e8e5f2;border-radius:18px;padding:16px 17px;min-height:100px;box-shadow:0 7px 20px rgba(74,54,123,.05)}
.admin-summary-label{font-size:.75rem;color:#858da0;font-weight:850}.admin-summary-value{font-size:1.65rem;color:#6b55e8;font-weight:1000;margin-top:5px}.admin-summary-note{font-size:.68rem;color:#a0a6b4;margin-top:3px}
.reader-admin-card{background:linear-gradient(135deg,#fff,#fbf8ff);border:1px solid #e6e1f0;border-radius:19px;padding:18px;box-shadow:0 8px 22px rgba(70,55,110,.05)}
.reader-admin-name{font-size:1.2rem;font-weight:1000;color:#23293d}.reader-admin-code{color:#8d5bd8;font-weight:900;font-size:.8rem}.reader-admin-meta{color:#737c90;font-size:.8rem;line-height:1.8;margin-top:8px}
.role-pill{display:inline-block;padding:5px 10px;border-radius:999px;background:#eee8ff;color:#6f4cd8;font-weight:900;font-size:.7rem}.status-pill{display:inline-block;padding:5px 10px;border-radius:999px;background:#e6fbf3;color:#15936f;font-weight:900;font-size:.7rem}.status-pill.locked{background:#ffe8ed;color:#dc4660}
.ai-fast-note{background:linear-gradient(135deg,#f3e8ff 0%,#fce7f3 100%)!important;border:1px solid #e9d5ff!important;border-radius:16px!important;padding:12px 18px!important;color:#6b21a8!important;font-size:.85rem!important;font-weight:700!important;margin-bottom:16px!important;box-shadow:0 4px 14px rgba(168,85,247,.08)!important}
.ai-answer-shell{background:#ffffff!important;border:1px solid #e5e7eb!important;border-radius:20px!important;padding:16px 20px!important;box-shadow:0 8px 25px rgba(0,0,0,.04)!important}
.floating-ai{width:60px!important;height:60px!important;min-width:60px!important;min-height:60px!important;right:24px!important;bottom:24px!important;background:linear-gradient(135deg,#6366f1 0%,#8b5cf6 50%,#ec4899 100%)!important;box-shadow:0 12px 30px rgba(139,92,246,.45)!important;border-radius:50%!important;display:flex!important;align-items:center!important;justify-content:center!important;transition:all .25s ease!important}
.floating-ai:hover{transform:scale(1.08) translateY(-2px)!important;box-shadow:0 16px 36px rgba(139,92,246,.6)!important}
div[role="dialog"]{position:fixed!important;right:22px!important;bottom:22px!important;left:auto!important;top:auto!important;transform:none!important;width:min(440px,calc(100vw - 32px))!important;max-width:440px!important;max-height:80vh!important;overflow-y:auto!important;background:rgba(20,18,30,.96)!important;backdrop-filter:blur(16px)!important;border:1px solid rgba(139,92,246,.35)!important;border-radius:24px!important;box-shadow:0 28px 75px rgba(0,0,0,.55)!important}
div[role="dialog"] [data-testid="stButton"] button{background:rgba(255,255,255,.07)!important;border:1px solid rgba(255,255,255,.14)!important;color:#f3f4f6!important;min-height:44px!important;border-radius:12px!important;font-weight:700!important;transition:all .2s ease!important}
div[role="dialog"] [data-testid="stButton"] button:hover{border-color:#a855f7!important;background:rgba(168,85,247,.2)!important;color:#fff!important;transform:translateY(-1px)!important}
div[role="dialog"] [data-testid="stButton"] button[kind="primary"]{background:linear-gradient(135deg,#6366f1,#8b5cf6,#ec4899)!important;border:0!important;box-shadow:0 4px 15px rgba(99,102,241,.35)!important}
div[role="dialog"] input{background:rgba(255,255,255,.08)!important;border-color:rgba(255,255,255,.18)!important;color:#fff!important;border-radius:14px!important}
.chat-popup-head{margin:-1rem -1rem 16px -1rem!important;padding:16px 20px!important;background:linear-gradient(135deg,#6366f1 0%,#8b5cf6 50%,#d946ef 100%)!important;border-radius:22px 22px 0 0!important;color:#fff!important;font-size:1.15rem!important;font-weight:900!important;box-shadow:0 4px 15px rgba(99,102,241,.3)!important}
.chat-popup-bot{width:68px!important;height:68px!important;background:linear-gradient(135deg,#8b5cf6,#ec4899)!important;border:3px solid #f3e8ff!important;box-shadow:0 8px 24px rgba(139,92,246,.35)!important;border-radius:50%!important;display:flex!important;align-items:center!important;justify-content:center!important;font-size:2rem!important;margin:6px auto 10px!important}

/* ===== EXPORT & REPORT CARDS UI ===== */
.export-card {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 22px !important;
    padding: 28px 22px 22px 22px !important;
    text-align: center !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.035) !important;
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: space-between !important;
    min-height: 290px !important;
    transition: all 0.25s ease !important;
    margin-bottom: 20px !important;
}
.export-card:hover {
    transform: translateY(-3px) !important;
    box-shadow: 0 16px 36px rgba(0, 0, 0, 0.07) !important;
    border-color: #cbd5e1 !important;
}
.export-card-icon {
    width: 64px !important;
    height: 64px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin: 0 auto 12px auto !important;
}
.export-card-title {
    font-size: 1.12rem !important;
    font-weight: 850 !important;
    color: #0f172a !important;
    margin-bottom: 8px !important;
    line-height: 1.35 !important;
}
.export-card-desc {
    font-size: 0.86rem !important;
    color: #64748b !important;
    line-height: 1.5 !important;
    margin-bottom: 18px !important;
}
body:has(.dark-theme-marker) .export-card {
    background: #151922 !important;
    border-color: #2d3748 !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2) !important;
}
body:has(.dark-theme-marker) .export-card-title {
    color: #f8fafc !important;
}
body:has(.dark-theme-marker) .export-card-desc {
    color: #94a3b8 !important;
}

.st-key-exp_books_btn button {
    background: #10b981 !important;
    color: #ffffff !important;
    border: none !important;
    font-weight: 850 !important;
    border-radius: 12px !important;
    min-height: 46px !important;
    font-size: 0.94rem !important;
    box-shadow: 0 4px 14px rgba(16, 185, 129, 0.28) !important;
}
.st-key-exp_books_btn button:hover {
    background: #059669 !important;
    color: #ffffff !important;
}

.st-key-exp_readers_btn button {
    background: #06b6d4 !important;
    color: #ffffff !important;
    border: none !important;
    font-weight: 850 !important;
    border-radius: 12px !important;
    min-height: 46px !important;
    font-size: 0.94rem !important;
    box-shadow: 0 4px 14px rgba(6, 182, 212, 0.28) !important;
}
.st-key-exp_readers_btn button:hover {
    background: #0284c7 !important;
    color: #ffffff !important;
}

.st-key-exp_loans_btn button {
    background: #f59e0b !important;
    color: #ffffff !important;
    border: none !important;
    font-weight: 850 !important;
    border-radius: 12px !important;
    min-height: 46px !important;
    font-size: 0.94rem !important;
    box-shadow: 0 4px 14px rgba(245, 158, 11, 0.28) !important;
}
.st-key-exp_loans_btn button:hover {
    background: #d97706 !important;
    color: #ffffff !important;
}

.st-key-exp_print_btn button {
    background: #4f46e5 !important;
    color: #ffffff !important;
    border: none !important;
    font-weight: 850 !important;
    border-radius: 12px !important;
    min-height: 46px !important;
    font-size: 0.94rem !important;
    box-shadow: 0 4px 14px rgba(79, 70, 229, 0.28) !important;
}
.st-key-exp_print_btn button:hover {
    background: #4338ca !important;
    color: #ffffff !important;
}

.st-key-exp_res_btn button {
    background: #8b5cf6 !important;
    color: #ffffff !important;
    border: none !important;
    font-weight: 850 !important;
    border-radius: 12px !important;
    min-height: 46px !important;
    font-size: 0.94rem !important;
    box-shadow: 0 4px 14px rgba(139, 92, 246, 0.28) !important;
}
.st-key-exp_res_btn button:hover {
    background: #7c3aed !important;
    color: #ffffff !important;
}

.st-key-exp_fines_btn button {
    background: #ef4444 !important;
    color: #ffffff !important;
    border: none !important;
    font-weight: 850 !important;
    border-radius: 12px !important;
    min-height: 46px !important;
    font-size: 0.94rem !important;
    box-shadow: 0 4px 14px rgba(239, 68, 68, 0.28) !important;
}
.st-key-exp_fines_btn button:hover {
    background: #dc2626 !important;
    color: #ffffff !important;
}



/* ===== V15 FIXED SIDEBAR: top + bottom fixed, center scrolls ===== */
section[data-testid="stSidebar"]{
    background:#fff!important;
    border-right:1px solid #e9e6f2!important;
}
section[data-testid="stSidebar"] > div:first-child{
    height:100vh!important;
    overflow:hidden!important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]{
    height:100vh!important;
    min-height:0!important;
    display:flex!important;
    flex-direction:column!important;
    overflow:hidden!important;
    padding:14px 12px 12px!important;
    gap:0!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_top_fixed{
    flex:0 0 auto!important;
    padding:2px 5px 10px!important;
    background:#fff!important;
    position:relative!important;
    z-index:3!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll{
    flex:1 1 auto!important;
    min-height:0!important;
    overflow-y:auto!important;
    overflow-x:hidden!important;
    padding:2px 7px 12px 5px!important;
    scrollbar-width:thin!important;
    scrollbar-color:#c9c6d5 transparent!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll::-webkit-scrollbar{width:5px!important;}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll::-webkit-scrollbar-track{background:transparent!important;}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll::-webkit-scrollbar-thumb{background:#c9c6d5!important;border-radius:99px!important;}
section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed{
    flex:0 0 auto!important;
    padding:10px 5px 2px!important;
    background:#fff!important;
    border-top:1px solid #ece9f3!important;
    box-shadow:0 -8px 18px rgba(60,50,100,.035)!important;
    position:relative!important;
    z-index:4!important;
}
section[data-testid="stSidebar"] .side-brand{
    padding:8px 4px 12px!important;
    border-bottom:1px solid #efedf4!important;
    margin-bottom:12px!important;
}
section[data-testid="stSidebar"] .profile-card{
    border-radius:18px!important;
    border:1px solid #e9e6f2!important;
    box-shadow:0 7px 18px rgba(71,57,110,.045)!important;
    padding:14px 14px 13px!important;
    margin-bottom:10px!important;
}
section[data-testid="stSidebar"] .profile-name{
    color:#172037!important;
    font-size:.98rem!important;
    font-weight:950!important;
}
section[data-testid="stSidebar"] .role-chip{
    background:#ffe7ee!important;
    color:#ef4f73!important;
    font-weight:950!important;
}
section[data-testid="stSidebar"] .side-group{
    color:#9b9fb4!important;
    font-size:.72rem!important;
    font-weight:950!important;
    letter-spacing:1.45px!important;
    padding:15px 8px 8px!important;
    margin:0!important;
}
section[data-testid="stSidebar"] .stButton{margin-bottom:6px!important;}
section[data-testid="stSidebar"] .stButton>button{
    justify-content:flex-start!important;
    text-align:left!important;
    min-height:52px!important;
    border-radius:14px!important;
    padding:10px 13px!important;
    font-size:.91rem!important;
    font-weight:850!important;
    line-height:1.25!important;
    border:1px solid transparent!important;
    background:#fff!important;
    color:#36435c!important;
    box-shadow:none!important;
    white-space:normal!important;
}
section[data-testid="stSidebar"] .stButton>button:hover{
    background:#f8f5ff!important;
    color:#6947d9!important;
    border-color:#e6ddfb!important;
    transform:translateX(1px)!important;
}
section[data-testid="stSidebar"] .stButton>button[kind="primary"]{
    background:linear-gradient(90deg,#635cf3 0%,#7d5df1 48%,#df43b5 100%)!important;
    color:#fff!important;
    border-color:transparent!important;
    box-shadow:0 10px 24px rgba(112,82,230,.17)!important;
    font-weight:950!important;
}
section[data-testid="stSidebar"] .stButton>button[kind="primary"] *{color:#fff!important;}
section[data-testid="stSidebar"] .st-key-sidebar_top_fixed .stButton>button{
    min-height:50px!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed .stButton>button{
    min-height:45px!important;
    border:1px solid #e7e3ef!important;
    background:#fff!important;
    box-shadow:none!important;
    font-size:.87rem!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed .stButton>button:hover{
    background:#f8f5ff!important;
    border-color:#d9cef7!important;
}
.sidebar-fixed-note{
    color:#a0a4b5;
    font-size:.68rem;
    text-align:center;
    margin-top:4px;
}
@media(max-height:720px){
    section[data-testid="stSidebar"] .stButton>button{min-height:46px!important;font-size:.84rem!important;}
    section[data-testid="stSidebar"] .side-group{padding-top:10px!important;}
    section[data-testid="stSidebar"] .profile-card{padding:10px 12px!important;}
}

/* ===== V16 CHAT OPEN FIX + SEARCH UI ===== */
.search-result-note{margin:12px 0 16px;padding:12px 15px;border-radius:14px;background:linear-gradient(90deg,#f3efff,#fff2fa);border:1px solid #e5dcf8;color:#644f86;font-size:.82rem;line-height:1.55}
.catalog-admin-title{font-size:.88rem;font-weight:950;color:#252b40;line-height:1.35;margin-top:7px;min-height:2.35em}.catalog-admin-meta{font-size:.72rem;color:#80899b;line-height:1.5;margin-top:5px}
.chat-history-title{font-size:.75rem;font-weight:900;letter-spacing:1px;color:#c0b3d5;margin:14px 0 8px;text-transform:uppercase}
.chat-bubble-user{margin:8px 0 8px 15%!important;padding:11px 16px!important;border-radius:18px 18px 4px 18px!important;background:linear-gradient(135deg,#6366f1,#8b5cf6)!important;color:#ffffff!important;font-size:.88rem!important;line-height:1.5!important;box-shadow:0 4px 14px rgba(99,102,241,.25)!important}
.chat-bubble-ai{margin:8px 15% 8px 0!important;padding:12px 16px!important;border-radius:18px 18px 18px 4px!important;background:rgba(255,255,255,.08)!important;border:1px solid rgba(255,255,255,.14)!important;color:#f3f4f6!important;font-size:.88rem!important;line-height:1.55!important;box-shadow:0 4px 16px rgba(0,0,0,.15)!important}
.chat-popup-sub{color:#d7ccdf!important;font-size:.82rem!important;margin-top:4px!important}
/* Force Streamlit modal to behave like Waka's bottom-right assistant rather than a centered modal. */
div[data-baseweb="modal"]{align-items:flex-end!important;justify-content:flex-end!important;padding:0 18px 18px 0!important}
div[data-baseweb="modal"]>div{margin:0!important;align-self:flex-end!important}
div[data-testid="stDialog"]{align-items:flex-end!important;justify-content:flex-end!important}
div[data-testid="stDialog"] div[role="dialog"]{margin:0 18px 18px 0!important;position:relative!important;right:auto!important;bottom:auto!important;left:auto!important;top:auto!important;transform:none!important}
@media(max-width:700px){div[data-baseweb="modal"]{padding:0!important}div[data-testid="stDialog"] div[role="dialog"]{margin:0!important;width:100vw!important;max-width:100vw!important;max-height:85vh!important;border-radius:22px 22px 0 0!important}}


/* ===== V19 SIDEBAR MATCH REFERENCE ===== */
section[data-testid="stSidebar"]{
    width:350px!important;
    min-width:350px!important;
    max-width:350px!important;
    background:#fff!important;
    border-right:1px solid #eceaf2!important;
    box-shadow:none!important;
}
section[data-testid="stSidebar"] > div:first-child{
    width:350px!important;
    height:100vh!important;
    overflow:hidden!important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]{
    height:100vh!important;
    display:flex!important;
    flex-direction:column!important;
    overflow:hidden!important;
    padding:20px 20px 10px!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_top_fixed{
    flex:0 0 auto!important;
    padding:0!important;
    background:#fff!important;
    z-index:5!important;
}
section[data-testid="stSidebar"] .side-brand{
    display:flex!important;
    align-items:center!important;
    gap:14px!important;
    padding:2px 0 18px!important;
    margin:0 0 16px!important;
    border-bottom:1px solid #eceaf1!important;
}
section[data-testid="stSidebar"] .brand-icon{
    width:54px!important;height:54px!important;border-radius:15px!important;
    font-size:1.55rem!important;flex:0 0 54px!important;
    background:linear-gradient(145deg,#715cff 5%,#9255ef 52%,#e448b9 100%)!important;
    box-shadow:0 10px 24px rgba(126,82,235,.18)!important;
}
section[data-testid="stSidebar"] .side-title{
    font-size:1.36rem!important;font-weight:1000!important;color:#101726!important;line-height:1.05!important;
}
section[data-testid="stSidebar"] .side-sub{
    font-size:.82rem!important;color:#66738a!important;margin-top:5px!important;
}
section[data-testid="stSidebar"] .profile-card{
    padding:17px 16px 15px!important;margin:0 0 14px!important;
    border:1px solid #ebe9ef!important;border-radius:18px!important;background:#fff!important;
    box-shadow:0 5px 16px rgba(70,57,105,.025)!important;
}
section[data-testid="stSidebar"] .profile-row{display:flex;align-items:center;gap:12px!important}
section[data-testid="stSidebar"] .profile-avatar{
    width:46px;height:46px;border-radius:50%;display:inline-flex;align-items:center;justify-content:center;
    background:#eeeaff;color:#675cf2;font-size:1.05rem;flex:0 0 46px;
}
section[data-testid="stSidebar"] .role-chip{
    display:inline-block!important;padding:4px 10px!important;border-radius:999px!important;
    background:#ffe5eb!important;color:#ff4b6d!important;font-size:.68rem!important;font-weight:1000!important;
}
section[data-testid="stSidebar"] .profile-name{
    font-size:.98rem!important;font-weight:1000!important;color:#101726!important;margin-top:5px!important;line-height:1.25!important;
}
section[data-testid="stSidebar"] .profile-user{margin:7px 0 0 58px!important;font-size:.75rem!important;color:#98a0b0!important}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll{
    flex:1 1 auto!important;min-height:0!important;overflow-y:auto!important;overflow-x:hidden!important;
    padding:3px 5px 14px 0!important;margin-right:-5px!important;
    scrollbar-width:thin!important;scrollbar-color:#d0d3df transparent!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll::-webkit-scrollbar{width:5px!important}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll::-webkit-scrollbar-track{background:transparent!important}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll::-webkit-scrollbar-thumb{background:#cfd2df!important;border-radius:999px!important}
section[data-testid="stSidebar"] .side-group{
    color:#9aa0b6!important;font-size:.68rem!important;font-weight:1000!important;letter-spacing:1.3px!important;
    padding:10px 10px 4px!important;margin:0!important;text-transform:uppercase!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll .stButton{margin:0 0 3px!important}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll .stButton>button{
    min-height:42px!important;border:1px solid #e2e8f0!important;border-radius:10px!important;background:#f8fafc!important;
    color:#334155!important;box-shadow:none!important;justify-content:flex-start!important;text-align:left!important;
    padding:7px 12px!important;font-size:.89rem!important;font-weight:700!important;line-height:1.3!important;
    transition:all 0.2s ease!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll .stButton>button:hover{
    background:#f1f5f9!important;color:#4f46e5!important;border-color:#cbd5e1!important;transform:none!important;
}
/* Các mục quản lý đang chọn: nền xanh tím như ảnh mẫu. */
section[data-testid="stSidebar"] .st-key-sidebar_core_group .stButton>button[kind="primary"],
section[data-testid="stSidebar"] .st-key-sidebar_home_group .stButton>button[kind="primary"]{
    background:linear-gradient(90deg,#6366f1 0%,#4f46e5 100%)!important;color:#fff!important;
    box-shadow:0 5px 14px rgba(99,102,241,.22)!important;border:0!important;font-weight:900!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_ai_group .stButton>button[kind="primary"],
section[data-testid="stSidebar"] .st-key-sidebar_ai_group .stButton>button[data-testid="stBaseButton-primary"]{
    background:linear-gradient(90deg,#6c5cf2 0%,#a44de7 50%,#df43b4 100%)!important;color:#fff!important;border:0!important;
    box-shadow:0 5px 16px rgba(164,77,231,.28)!important;font-weight:900!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_ai_group .stButton>button[kind="primary"] *,
section[data-testid="stSidebar"] .st-key-sidebar_ai_group .stButton>button[data-testid="stBaseButton-primary"] *{color:#fff!important}
section[data-testid="stSidebar"] .st-key-sidebar_report_group .stButton>button[kind="primary"]{
    background:linear-gradient(90deg,#059669 0%,#10b981 100%)!important;color:#fff!important;border:0!important;
    box-shadow:0 5px 14px rgba(16,185,129,.22)!important;font-weight:900!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_report_group .stButton>button[kind="primary"] *{color:#fff!important}
section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed{
    flex:0 0 auto!important;background:#fff!important;border-top:1px solid #eceaf1!important;
    padding:12px 0 0!important;box-shadow:none!important;z-index:8!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed .stButton{margin:0 0 9px!important}
section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed .stButton>button{
    min-height:48px!important;background:#fff!important;border:1px solid #e7e5ec!important;border-radius:11px!important;
    color:#3b4b64!important;font-size:.91rem!important;font-weight:650!important;padding:9px 15px!important;
    justify-content:flex-start!important;box-shadow:none!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed .stButton>button:hover{
    background:#faf9fd!important;border-color:#ddd7eb!important;color:#5b52d6!important;
}
@media(max-width:900px){
  section[data-testid="stSidebar"],section[data-testid="stSidebar"]>div:first-child{width:330px!important;min-width:330px!important;max-width:330px!important}
}
@media(max-height:760px){
  section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]{padding-top:12px!important}
  section[data-testid="stSidebar"] .side-brand{padding-bottom:12px!important;margin-bottom:10px!important}
  section[data-testid="stSidebar"] .profile-card{padding:12px!important;margin-bottom:8px!important}
  section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll .stButton>button{min-height:50px!important;font-size:.9rem!important}
  section[data-testid="stSidebar"] .side-group{padding-top:12px!important}
}

/* ===== V17 BOOK MANAGEMENT UI ===== */
.books-page-marker{display:none}
.book-page-heading{font-size:1.58rem;font-weight:1000;color:#121827;line-height:1.1;margin:0 0 3px}
.book-page-sub{font-size:.84rem;color:#6f7b8f;margin:0}
.book-toolbar-note{font-size:.72rem;color:#8d96a8;margin-top:3px}
.book-kpi{background:#fff;border:1px solid #e2e7ef;border-radius:15px;padding:11px 14px;min-height:74px;box-shadow:0 5px 14px rgba(37,52,79,.035)}
.book-kpi-label{font-size:.69rem;font-weight:850;color:#8994a7;text-transform:uppercase;letter-spacing:.03em}
.book-kpi-value{font-size:1.28rem;font-weight:1000;color:#5f5cf1;margin-top:4px}
.book-kpi-note{font-size:.63rem;color:#9aa4b4;margin-top:1px}
.book-filter-shell{background:#edf2f7;border-radius:18px;padding:13px 14px 2px;margin:10px 0 14px}
.book-card-shell{background:#fff;border:1px solid #dfe5ed;border-radius:17px;overflow:hidden;box-shadow:0 5px 15px rgba(43,55,86,.06);margin-bottom:15px;min-height:515px}
.book-card-cover{width:100%;height:235px;object-fit:cover;display:block;background:#edf1f5}
.book-card-cover-empty{height:235px;display:flex;align-items:center;justify-content:center;font-size:4rem;background:linear-gradient(135deg,#f1eefb,#e9eef8)}
.book-card-body{padding:15px 17px 11px;min-height:218px}
.book-card-category{font-size:.70rem;font-weight:950;color:#625df3;text-transform:uppercase;letter-spacing:.02em;min-height:34px}
.book-card-title{font-size:1.02rem;font-weight:1000;color:#111827;line-height:1.24;margin:3px 0 5px;min-height:48px}
.book-card-author{font-size:.84rem;color:#516074;min-height:24px}
.book-card-divider{height:1px;background:#e8ecf1;margin:14px 0 11px}
.book-card-stock{display:flex;justify-content:space-between;gap:10px;font-size:.72rem;color:#8b97a9}
.book-card-footer{background:#eef1f4;padding:10px 11px 8px;border-top:1px solid #dde3ea}
.book-badge-stock{display:inline-flex;align-items:center;gap:4px}
.book-empty-msg{background:#fff;border:1px dashed #cfd7e3;border-radius:18px;padding:38px;text-align:center;color:#7d889b}
.book-list-row{background:#fff;border:1px solid #e1e6ed;border-radius:15px;padding:12px 14px;margin:8px 0}
.book-ai-result{background:linear-gradient(135deg,#f7f3ff,#fff3fa);border:1px solid #e4d8f7;border-radius:15px;padding:14px;color:#34384c}
/* make book page controls closer to the provided reference */
body:has(.books-page-marker) [data-testid="stMainBlockContainer"]{background:#eef3f8!important;max-width:none!important;padding-top:1.1rem!important}
body:has(.books-page-marker) [data-testid="stTextInputRootElement"],
body:has(.books-page-marker) [data-baseweb="select"]>div{border-radius:13px!important;background:#fff!important;border-color:#dbe2eb!important;min-height:48px!important}
body:has(.books-page-marker) div[data-testid="stButton"]>button{border-radius:11px!important;font-weight:850!important}
body:has(.books-page-marker) [class*="st-key-book_card_"]{background:#fff;border:1px solid #dfe5ed;border-radius:17px;padding:0 0 10px;overflow:hidden;box-shadow:0 5px 15px rgba(43,55,86,.06)}
body:has(.books-page-marker) [class*="st-key-book_card_"] [data-testid="stImage"] img{height:235px!important;object-fit:cover!important;border-radius:0!important}
body:has(.books-page-marker) [class*="st-key-book_card_"] [data-testid="stVerticalBlock"]{gap:.38rem}
body:has(.books-page-marker) [class*="st-key-book_card_"] div[data-testid="stButton"]>button{min-height:38px!important;font-size:.78rem!important}


/* ===== V18: compact staff layout + reader management reference UI ===== */
body:has(section[data-testid="stSidebar"]) [data-testid="stMainBlockContainer"]{
  padding-top:.35rem!important;
  padding-bottom:1rem!important;
}
body:has(.reader-mgmt-marker) [data-testid="stMainBlockContainer"]{
  background:#eef3f8!important;
  max-width:none!important;
  padding-left:2rem!important;
  padding-right:2rem!important;
}
body:has(.reader-mgmt-marker) header[data-testid="stHeader"]{
  height:0!important;min-height:0!important;background:transparent!important;
}
.reader-mgmt-marker{display:none}
.reader-page-heading{font-size:1.62rem;font-weight:950;color:#131a2a;line-height:1.1;margin-top:5px}
.reader-page-sub{font-size:.86rem;color:#64748b;margin-top:5px}
.reader-filter-shell{margin:14px 0 17px}
.reader-table-card{background:#fff;border:1px solid #e3e8ef;border-radius:22px;padding:13px 18px 8px;box-shadow:0 10px 24px rgba(55,67,97,.07)}
.reader-table-head{color:#526076;font-size:.82rem;font-weight:900;padding:8px 0 10px;border-bottom:1px solid #e6e9ef}
.reader-row{padding:13px 0 11px;border-bottom:1px solid #e7e9ee;color:#1b2433;font-size:.83rem;min-height:62px}
.reader-row:last-child{border-bottom:0}
.reader-code{font-weight:900;color:#20283a}
.reader-name{font-weight:900;color:#151c2a;font-size:.88rem}.reader-user{font-size:.70rem;color:#6f7a8c;margin-top:3px}
.reader-contact{line-height:1.55;color:#283548}.reader-date{font-size:.80rem;color:#283548}
.reader-pill{display:inline-flex;align-items:center;justify-content:center;padding:6px 12px;border-radius:999px;font-size:.72rem;font-weight:900;white-space:nowrap}
.reader-pill.type{background:#dff7ff;border:1px solid #83dbef;color:#00a9d5}
.reader-pill.active{background:#dff8ee;border:1px solid #96dfc3;color:#13b986}
.reader-pill.locked{background:#ffe8ec;border:1px solid #f5a8b4;color:#e84d68}
.reader-actions [data-testid="stButton"] button{min-height:34px!important;height:34px!important;padding:.18rem .55rem!important;border-radius:10px!important;font-size:.76rem!important}
.reader-empty{background:#fff;border:1px solid #e2e7ef;border-radius:20px;padding:38px;text-align:center;color:#7b879a}
body:has(.reader-mgmt-marker) [data-testid="stTextInputRootElement"],
body:has(.reader-mgmt-marker) [data-baseweb="select"]>div{background:#fff!important;border-color:#d8e0ea!important;border-radius:12px!important;min-height:48px!important}
body:has(.reader-mgmt-marker) div[data-testid="stButton"]>button{border-radius:11px!important;font-weight:850!important}



/* ===== V22 EXACT SIDEBAR REFERENCE ===== */
section[data-testid="stSidebar"]{
  width:355px!important;min-width:355px!important;max-width:355px!important;
  background:#fff!important;border-right:1px solid #e6e8ee!important;box-shadow:none!important;
}
section[data-testid="stSidebar"]>div:first-child{
  width:355px!important;min-width:355px!important;max-width:355px!important;height:100vh!important;overflow:hidden!important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]{
  height:100vh!important;min-height:0!important;display:flex!important;flex-direction:column!important;
  overflow:hidden!important;padding:30px 25px 10px 29px!important;gap:0!important;background:#fff!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_top_fixed{
  flex:0 0 auto!important;padding:0!important;margin:0!important;background:#fff!important;z-index:10!important;
}
section[data-testid="stSidebar"] .side-brand{
  display:flex!important;align-items:center!important;gap:16px!important;padding:7px 0 25px!important;
  margin:0 0 25px!important;border-bottom:1px solid #e9e9ef!important;
}
section[data-testid="stSidebar"] .brand-icon{
  width:55px!important;height:55px!important;min-width:55px!important;flex:0 0 55px!important;
  border-radius:15px!important;background:linear-gradient(145deg,#745CFF 4%,#9458F0 54%,#E248B7 100%)!important;
  display:flex!important;align-items:center!important;justify-content:center!important;
  box-shadow:0 9px 23px rgba(120,78,229,.17)!important;
}
section[data-testid="stSidebar"] .brand-icon svg{display:block!important}
section[data-testid="stSidebar"] .side-title{
  display:flex!important;align-items:center!important;gap:5px!important;white-space:nowrap!important;
  color:#0d1627!important;font-size:1.40rem!important;line-height:1.05!important;font-weight:1000!important;letter-spacing:-.45px!important;
}
section[data-testid="stSidebar"] .ai-badge{
  display:inline-flex!important;align-items:center!important;justify-content:center!important;
  font-size:.61rem!important;line-height:1!important;font-weight:1000!important;color:#fff!important;
  background:linear-gradient(135deg,#8a5af2,#da45ba)!important;border-radius:6px!important;padding:4px 6px!important;margin-left:1px!important;
}
section[data-testid="stSidebar"] .side-sub{
  color:#50617a!important;font-size:.86rem!important;line-height:1.1!important;margin-top:7px!important;font-weight:500!important;
}
section[data-testid="stSidebar"] .profile-card{
  width:100%!important;box-sizing:border-box!important;margin:0 0 15px!important;padding:20px 17px!important;
  min-height:99px!important;border:1px solid #e7e7ed!important;border-radius:17px!important;background:#fff!important;
  box-shadow:0 4px 13px rgba(68,63,92,.025)!important;
}
section[data-testid="stSidebar"] .profile-row{display:flex!important;align-items:center!important;gap:13px!important}
section[data-testid="stSidebar"] .profile-avatar{
  width:48px!important;height:48px!important;flex:0 0 48px!important;border-radius:50%!important;
  display:flex!important;align-items:center!important;justify-content:center!important;background:#eeebff!important;color:#675cf2!important;
}
section[data-testid="stSidebar"] .profile-avatar svg{display:block!important}
section[data-testid="stSidebar"] .role-chip{
  display:inline-flex!important;align-items:center!important;min-height:26px!important;padding:4px 10px!important;
  border-radius:999px!important;background:#ffe7ec!important;color:#ff4b69!important;font-size:.69rem!important;
  line-height:1!important;font-weight:1000!important;letter-spacing:.1px!important;
}
section[data-testid="stSidebar"] .profile-name{
  margin-top:7px!important;color:#101827!important;font-size:1rem!important;line-height:1.18!important;font-weight:1000!important;white-space:nowrap!important;
}
section[data-testid="stSidebar"] .profile-user{display:none!important}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll{
  flex:1 1 auto!important;min-height:0!important;overflow-y:auto!important;overflow-x:hidden!important;
  margin:0 -3px 0 0!important;padding:2px 7px 14px 0!important;scrollbar-width:thin!important;scrollbar-color:#d2d5df transparent!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll::-webkit-scrollbar{width:5px!important}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll::-webkit-scrollbar-track{background:transparent!important}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll::-webkit-scrollbar-thumb{background:#d2d5df!important;border-radius:999px!important}
section[data-testid="stSidebar"] .side-group{
  margin:0!important;padding:19px 14px 10px!important;color:#9ba3b8!important;font-size:.74rem!important;
  line-height:1!important;font-weight:1000!important;letter-spacing:1.65px!important;text-transform:uppercase!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll .stButton{margin:0 0 3px!important}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll .stButton>button{
  width:100%!important;min-height:56px!important;height:auto!important;padding:11px 16px!important;border:0!important;
  border-radius:11px!important;background:#fff!important;box-shadow:none!important;color:#314058!important;
  justify-content:flex-start!important;text-align:left!important;font-size:.98rem!important;font-weight:650!important;line-height:1.42!important;
  gap:11px!important;white-space:normal!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll .stButton>button [data-testid="stIconMaterial"]{
  color:#40516a!important;font-size:1.55rem!important;min-width:26px!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll .stButton>button:hover{
  background:#faf9fd!important;color:#5d56d9!important;transform:none!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_core_group .stButton>button[kind="primary"],
section[data-testid="stSidebar"] .st-key-sidebar_home_group .stButton>button[kind="primary"]{
  background:linear-gradient(90deg,#625CF2 0%,#6667F1 100%)!important;color:#fff!important;
  font-weight:900!important;box-shadow:0 8px 18px rgba(87,82,220,.15)!important;border:0!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_core_group .stButton>button[kind="primary"] [data-testid="stIconMaterial"],
section[data-testid="stSidebar"] .st-key-sidebar_home_group .stButton>button[kind="primary"] [data-testid="stIconMaterial"]{color:#fff!important}
section[data-testid="stSidebar"] .st-key-sidebar_ai_group .stButton>button[kind="primary"],
section[data-testid="stSidebar"] .st-key-sidebar_ai_group .stButton>button[data-testid="stBaseButton-primary"]{
  background:linear-gradient(90deg,#6c5cf2 0%,#a44de7 50%,#df43b4 100%)!important;color:#fff!important;border:0!important;box-shadow:0 8px 22px rgba(164,77,231,.25)!important;font-weight:950!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_ai_group .stButton>button[kind="primary"] *,
section[data-testid="stSidebar"] .st-key-sidebar_ai_group .stButton>button[data-testid="stBaseButton-primary"] *{color:#fff!important}
section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed{
  flex:0 0 auto!important;margin:0!important;padding:11px 0 0!important;background:#fff!important;
  border-top:1px solid #e9e9ef!important;box-shadow:none!important;z-index:12!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed .stButton{margin:0 0 9px!important}
section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed .stButton>button{
  width:100%!important;min-height:48px!important;padding:9px 15px!important;border:1px solid #e5e5eb!important;
  border-radius:10px!important;background:#fff!important;color:#36475f!important;box-shadow:none!important;
  justify-content:flex-start!important;text-align:left!important;font-size:.94rem!important;font-weight:600!important;gap:10px!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed .stButton>button [data-testid="stIconMaterial"]{color:#3e536d!important;font-size:1.35rem!important}
section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed .stButton>button:hover{background:#faf9fd!important;border-color:#ddd8e7!important;color:#5d56d9!important}
@media(max-width:900px){
  section[data-testid="stSidebar"],section[data-testid="stSidebar"]>div:first-child{width:330px!important;min-width:330px!important;max-width:330px!important}
  section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]{padding-left:22px!important;padding-right:20px!important}
}
@media(max-height:760px){
  section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]{padding-top:18px!important}
  section[data-testid="stSidebar"] .side-brand{padding-bottom:17px!important;margin-bottom:15px!important}
  section[data-testid="stSidebar"] .profile-card{padding:13px 14px!important;min-height:82px!important}
  section[data-testid="stSidebar"] .profile-avatar{width:42px!important;height:42px!important;flex-basis:42px!important}
  section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll .stButton>button{min-height:50px!important;font-size:.91rem!important}
  section[data-testid="stSidebar"] .side-group{padding-top:13px!important}
}

/* Fixed tools + real light/dark theme */
section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed .stButton>button[kind="primary"]{background:linear-gradient(90deg,#625cf3,#8a5cf6)!important;color:#fff!important;border-color:transparent!important;font-weight:900!important;box-shadow:0 8px 18px rgba(91,84,220,.14)!important;}
section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed .stButton>button[kind="primary"] [data-testid="stIconMaterial"]{color:#fff!important}
.dark-theme-marker{display:none!important}
body:has(.dark-theme-marker) .stApp{background:#10131a!important;color:#e8ecf5!important}
body:has(.dark-theme-marker) header[data-testid="stHeader"]{background:rgba(16,19,26,.88)!important}
body:has(.dark-theme-marker) section[data-testid="stSidebar"]{background:#151922!important;border-right:1px solid #292f3a!important}
body:has(.dark-theme-marker) section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],body:has(.dark-theme-marker) section[data-testid="stSidebar"] .st-key-sidebar_top_fixed,body:has(.dark-theme-marker) section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll,body:has(.dark-theme-marker) section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed{background:#151922!important}
body:has(.dark-theme-marker) section[data-testid="stSidebar"] .side-title,body:has(.dark-theme-marker) section[data-testid="stSidebar"] .profile-name{color:#f5f7fb!important}
body:has(.dark-theme-marker) section[data-testid="stSidebar"] .side-sub{color:#9ca6b8!important}
body:has(.dark-theme-marker) section[data-testid="stSidebar"] .profile-card{background:#1b202b!important;border-color:#303744!important}
body:has(.dark-theme-marker) section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll .stButton>button,body:has(.dark-theme-marker) section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed .stButton>button{background:#171c26!important;color:#dbe2ef!important;border-color:#303744!important}
body:has(.dark-theme-marker) section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll .stButton>button:hover,body:has(.dark-theme-marker) section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed .stButton>button:hover{background:#232938!important;color:#c6b7ff!important;border-color:#47405f!important}
body:has(.dark-theme-marker) section[data-testid="stSidebar"] .side-group{color:#8f98aa!important}
body:has(.dark-theme-marker) section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed{border-top-color:#2d3340!important}
body:has(.dark-theme-marker) .page-title,body:has(.dark-theme-marker) h1,body:has(.dark-theme-marker) h2,body:has(.dark-theme-marker) h3{color:#f3f5fb!important}
body:has(.dark-theme-marker) .page-sub,body:has(.dark-theme-marker) .small-muted{color:#9ca6b8!important}
body:has(.dark-theme-marker) .panel,body:has(.dark-theme-marker) .metric-card,body:has(.dark-theme-marker) .admin-summary-card,body:has(.dark-theme-marker) .reader-table-card,body:has(.dark-theme-marker) .reader-panel,body:has(.dark-theme-marker) .reader-profile-box,body:has(.dark-theme-marker) .book-card-shell,body:has(.dark-theme-marker) .book-list-row,body:has(.dark-theme-marker) [data-testid="stMetric"]{background:#191e28!important;border-color:#303744!important;color:#e8ecf5!important}
body:has(.dark-theme-marker) [data-testid="stTextInput"] input,body:has(.dark-theme-marker) [data-testid="stTextArea"] textarea,body:has(.dark-theme-marker) [data-baseweb="select"]>div{background:#171c26!important;color:#edf1f8!important;border-color:#343b48!important}
body:has(.dark-theme-marker) [data-testid="stDataFrame"]{background:#171c26!important;color:#e8ecf5!important}



/* ===== V26 FINAL SIDEBAR & DARK THEME REFINEMENT ===== */
section[data-testid="stSidebar"]{
  background:#fff!important;
  border-right:1px solid #e8e8ef!important;
  box-shadow:none!important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarCollapseButton"]{display:none!important;}
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]{
  padding:18px 22px 10px 22px!important;
  margin-top:-48px!important;
  height:calc(100vh + 48px)!important;
  min-height:0!important;
  display:flex!important;
  flex-direction:column!important;
  gap:0!important;
  overflow:hidden!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_top_fixed{
  flex:0 0 auto!important;
  padding:0!important;
  margin:0!important;
}
section[data-testid="stSidebar"] .side-brand{
  display:flex!important;
  align-items:center!important;
  gap:12px!important;
  padding:0 0 16px!important;
  margin:0 0 14px!important;
  border-bottom:1px solid #ececf2!important;
}
section[data-testid="stSidebar"] .brand-icon{
  width:48px!important;height:48px!important;min-width:48px!important;
  border-radius:14px!important;
  display:flex!important;align-items:center!important;justify-content:center!important;
  background:linear-gradient(145deg,#735cfb 3%,#9458ef 55%,#df45b8 100%)!important;
  box-shadow:0 8px 20px rgba(118,77,228,.16)!important;
}
section[data-testid="stSidebar"] .side-title{
  color:#0b1424!important;
  font-size:1.2rem!important;
  line-height:1.1!important;
  font-weight:1000!important;
  letter-spacing:-.4px!important;
  white-space:nowrap!important;
}
section[data-testid="stSidebar"] .side-sub{
  margin-top:4px!important;
  color:#465b78!important;
  font-size:.8rem!important;
  font-weight:500!important;
}
section[data-testid="stSidebar"] .profile-card{
  margin:0 0 14px!important;
  padding:14px 14px!important;
  min-height:85px!important;
  border-radius:16px!important;
  border:1px solid #e7e7ee!important;
  background:#fff!important;
  box-shadow:none!important;
}
section[data-testid="stSidebar"] .profile-avatar{
  width:42px!important;height:42px!important;flex:0 0 42px!important;
  background:#efebff!important;
}
section[data-testid="stSidebar"] .profile-row{gap:10px!important;}
section[data-testid="stSidebar"] .role-chip{
  padding:3px 9px!important;
  background:#ffe7ed!important;
  color:#ff4768!important;
  font-size:.65rem!important;
  font-weight:1000!important;
}
section[data-testid="stSidebar"] .profile-name{
  margin-top:5px!important;
  color:#0e1728!important;
  font-size:.92rem!important;
  font-weight:1000!important;
  white-space:nowrap!important;
}
/* Center menu section scrolls all the way down to bottom items */
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll{
  flex:1 1 auto!important;
  min-height:0!important;
  overflow-y:auto!important;
  overflow-x:hidden!important;
  padding:0 4px 20px 0!important;
  margin:0!important;
  scrollbar-width:thin!important;
  scrollbar-color:#cfd3dd transparent!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll::-webkit-scrollbar{width:5px!important;}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll::-webkit-scrollbar-thumb{background:#cfd3dd!important;border-radius:999px!important;}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll [data-testid="stVerticalBlock"],
section[data-testid="stSidebar"] .st-key-sidebar_core_group [data-testid="stVerticalBlock"],
section[data-testid="stSidebar"] .st-key-sidebar_ai_group [data-testid="stVerticalBlock"],
section[data-testid="stSidebar"] .st-key-sidebar_report_group [data-testid="stVerticalBlock"]{
  gap:0!important;
  row-gap:0!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll .stElementContainer{
  margin:0!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll .stButton{
  margin:0 0 4px!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll .stButton>button{
  width:100%!important;
  min-height:50px!important;
  padding:9px 13px!important;
  border:0!important;
  border-radius:11px!important;
  background:#fff!important;
  color:#31425d!important;
  box-shadow:none!important;
  justify-content:flex-start!important;
  text-align:left!important;
  gap:10px!important;
  font-size:.91rem!important;
  font-weight:650!important;
  line-height:1.35!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll .stButton>button [data-testid="stIconMaterial"]{
  color:#3d536d!important;
  font-size:1.35rem!important;
  min-width:24px!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll .stButton>button:hover{
  background:#f7f6fb!important;
  color:#5e56df!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_core_group button[kind="primary"],
section[data-testid="stSidebar"] .st-key-sidebar_core_group button[data-testid="stBaseButton-primary"]{
  background:#6463f1!important;
  color:#fff!important;
  border:1px solid #1f2440!important;
  box-shadow:0 7px 16px rgba(91,87,219,.14)!important;
  font-weight:900!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_core_group button[kind="primary"] *,
section[data-testid="stSidebar"] .st-key-sidebar_core_group button[data-testid="stBaseButton-primary"] *{
  color:#fff!important;
}
section[data-testid="stSidebar"] .side-group{
  margin:0!important;
  padding:15px 10px 7px!important;
  color:#98a0b5!important;
  font-size:.72rem!important;
  font-weight:1000!important;
  letter-spacing:1.45px!important;
  text-transform:uppercase!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_ai_group button[kind="primary"],
section[data-testid="stSidebar"] .st-key-sidebar_ai_group button[data-testid="stBaseButton-primary"]{
  background:linear-gradient(90deg,#6c5cf2 0%,#a44de7 50%,#df43b4 100%)!important;
  color:#ffffff!important;
  border:0!important;
  box-shadow:0 8px 22px rgba(164,77,231,.25)!important;
  font-weight:950!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_ai_group button[kind="primary"] *,
section[data-testid="stSidebar"] .st-key-sidebar_ai_group button[data-testid="stBaseButton-primary"] *{
  color:#ffffff!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed{
  flex:0 0 auto!important;
  padding:10px 0 0!important;
  margin:0!important;
  background:#fff!important;
  border-top:1px solid #ececf1!important;
  box-shadow:none!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed [data-testid="stVerticalBlock"]{gap:0!important;}
section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed .stButton{margin:0 0 6px!important;}
section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed .stButton>button{
  min-height:45px!important;
  padding:8px 13px!important;
  border:1px solid #e5e5eb!important;
  border-radius:10px!important;
  background:#fff!important;
  color:#354761!important;
  box-shadow:none!important;
  justify-content:flex-start!important;
  font-size:.9rem!important;
  font-weight:600!important;
  gap:10px!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed .stButton>button [data-testid="stIconMaterial"]{
  color:#3e536d!important;font-size:1.25rem!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed button[kind="primary"],
section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed button[data-testid="stBaseButton-primary"]{
  background:#fff!important;color:#354761!important;border:1px solid #e5e5eb!important;box-shadow:none!important;font-weight:600!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed button[kind="primary"] *,
section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed button[data-testid="stBaseButton-primary"] *{color:#354761!important;}

/* ===== WAKA-STYLE COMPACT CHATBOT WIDGET ===== */
div[data-testid="stDialog"] div[role="dialog"]{
  width:min(370px,calc(100vw - 24px))!important;
  max-width:370px!important;
  max-height:540px!important;
  height:540px!important;
  background:#111318!important;
  color:#e2e8f0!important;
  border:1px solid #282e3d!important;
  border-radius:20px!important;
  box-shadow:0 20px 60px rgba(0,0,0,.75)!important;
  padding:0 16px 14px!important;
  overflow:hidden!important;
}
div[data-testid="stDialog"] div[role="dialog"] [data-testid="stDialogHeader"]{
  display:none!important;
}
div[role="dialog"] [data-testid="stMarkdownContainer"] p,
div[role="dialog"] [data-testid="stMarkdownContainer"] li,
div[role="dialog"] [data-testid="stMarkdownContainer"] span,
div[role="dialog"] label,
div[role="dialog"] caption{
  color:#e2e8f0!important;
}

.waka-head-bar{
  background:linear-gradient(135deg,#00b894 0%,#00cec9 100%)!important;
  padding:12px 16px!important;
  display:flex!important;
  align-items:center!important;
  justify-content:space-between!important;
  color:#ffffff!important;
  font-size:1rem!important;
  font-weight:800!important;
  box-shadow:0 4px 15px rgba(0,184,148,.25)!important;
  margin:-1rem -1rem 10px -1rem!important;
}
.waka-head-title{
  display:flex!important;
  align-items:center!important;
  gap:8px!important;
}
.waka-bot-avatar{
  width:32px!important;
  height:32px!important;
  border-radius:50%!important;
  background:rgba(255,255,255,.25)!important;
  display:inline-flex!important;
  align-items:center!important;
  justify-content:center!important;
  font-size:1.1rem!important;
}
.waka-status-badge{
  font-size:.68rem!important;
  background:rgba(0,0,0,.25)!important;
  padding:2px 8px!important;
  border-radius:99px!important;
  font-weight:700!important;
}
.waka-suggest-prompt{
  background:#00b894!important;
  color:#ffffff!important;
  font-size:.84rem!important;
  font-weight:700!important;
  padding:10px 14px!important;
  border-radius:18px!important;
  margin:8px 4px 10px!important;
  text-align:center!important;
  box-shadow:0 4px 12px rgba(0,184,148,.2)!important;
}
.waka-msg-user{
  margin:6px 4px 6px auto!important;
  max-width:82%!important;
  padding:9px 14px!important;
  border-radius:18px 18px 4px 18px!important;
  background:linear-gradient(135deg,#00b894,#00cec9)!important;
  color:#ffffff!important;
  font-size:.85rem!important;
  line-height:1.45!important;
  box-shadow:0 4px 12px rgba(0,184,148,.2)!important;
  word-break:break-word!important;
}
.waka-msg-ai-wrap{
  display:flex!important;
  align-items:flex-start!important;
  gap:8px!important;
  margin:8px 4px!important;
}
.waka-ai-avatar{
  width:32px!important;
  height:32px!important;
  flex:0 0 32px!important;
  border-radius:50%!important;
  background:linear-gradient(135deg,#1e2434,#2d364e)!important;
  border:2px solid #00b894!important;
  display:flex!important;
  align-items:center!important;
  justify-content:center!important;
  font-size:1.1rem!important;
}
.waka-msg-ai-box{
  background:#1a1e2b!important;
  border:1px solid #293144!important;
  color:#e2e8f0!important;
  border-radius:16px!important;
  padding:10px 14px!important;
  font-size:.85rem!important;
  line-height:1.5!important;
  box-shadow:0 4px 14px rgba(0,0,0,.25)!important;
  flex:1!important;
}
.waka-msg-ai-box *{
  color:#e2e8f0!important;
}
div[role="dialog"] [data-testid="stForm"]{
  background:#161a26!important;
  border:1px solid #293144!important;
  border-radius:18px!important;
  margin:6px 0!important;
  padding:4px 6px!important;
}
div[role="dialog"] input{
  background:transparent!important;
  border:0!important;
  color:#ffffff!important;
  font-size:.86rem!important;
}
div[role="dialog"] input::placeholder{
  color:#76849f!important;
}
div[role="dialog"] [data-testid="stFormSubmitButton"] button{
  background:linear-gradient(135deg,#00b894,#00cec9)!important;
  border:0!important;
  color:#ffffff!important;
  border-radius:14px!important;
  font-weight:800!important;
  min-height:36px!important;
}
div[role="dialog"] [data-testid="stButton"] button{
  background:#181d2b!important;
  border:1px solid #283044!important;
  color:#94a3b8!important;
  border-radius:12px!important;
  font-size:.78rem!important;
  min-height:36px!important;
}
div[role="dialog"] [data-testid="stButton"] button:hover{
  background:#232a3e!important;
  color:#00b894!important;
  border-color:#00b894!important;
}

/* ===== DARK THEME GLOBAL OVERRIDES ===== */
.dark-theme-marker{display:none!important}
body:has(.dark-theme-marker) .stApp{background:#0e1117!important;color:#e2e8f0!important}
body:has(.dark-theme-marker) header[data-testid="stHeader"]{background:rgba(14,17,23,.9)!important}
body:has(.dark-theme-marker) section[data-testid="stSidebar"]{
  background:#141824!important;
  border-right-color:#262d3e!important;
}
body:has(.dark-theme-marker) section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"],
body:has(.dark-theme-marker) section[data-testid="stSidebar"] .st-key-sidebar_top_fixed,
body:has(.dark-theme-marker) section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll,
body:has(.dark-theme-marker) section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed{
  background:#141824!important;
}
body:has(.dark-theme-marker) section[data-testid="stSidebar"] .side-title,
body:has(.dark-theme-marker) section[data-testid="stSidebar"] .profile-name{
  color:#f1f5f9!important;
}
body:has(.dark-theme-marker) section[data-testid="stSidebar"] .side-sub,
body:has(.dark-theme-marker) section[data-testid="stSidebar"] .side-group{
  color:#94a3b8!important;
}
body:has(.dark-theme-marker) section[data-testid="stSidebar"] .profile-card{
  background:#1b2030!important;
  border-color:#2b3448!important;
}
body:has(.dark-theme-marker) section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll .stButton>button,
body:has(.dark-theme-marker) section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed .stButton>button{
  background:#181d2c!important;
  color:#cbd5e1!important;
  border:1px solid #262e42!important;
}
body:has(.dark-theme-marker) section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll .stButton>button [data-testid="stIconMaterial"],
body:has(.dark-theme-marker) section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed .stButton>button [data-testid="stIconMaterial"]{
  color:#94a3b8!important;
}
body:has(.dark-theme-marker) section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll .stButton>button:hover,
body:has(.dark-theme-marker) section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed .stButton>button:hover{
  background:#22293e!important;
  color:#a78bfa!important;
  border-color:#3b4763!important;
}
body:has(.dark-theme-marker) section[data-testid="stSidebar"] .st-key-sidebar_core_group button[kind="primary"],
body:has(.dark-theme-marker) section[data-testid="stSidebar"] .st-key-sidebar_core_group button[data-testid="stBaseButton-primary"]{
  background:#6366f1!important;
  color:#ffffff!important;
  border-color:#8b5cf6!important;
}
body:has(.dark-theme-marker) section[data-testid="stSidebar"] .st-key-sidebar_core_group button[kind="primary"] *,
body:has(.dark-theme-marker) section[data-testid="stSidebar"] .st-key-sidebar_core_group button[data-testid="stBaseButton-primary"] *{
  color:#ffffff!important;
}
body:has(.dark-theme-marker) .page-title,
body:has(.dark-theme-marker) h1,
body:has(.dark-theme-marker) h2,
body:has(.dark-theme-marker) h3{
  color:#f8fafc!important;
}
body:has(.dark-theme-marker) .page-sub,
body:has(.dark-theme-marker) .small-muted{
  color:#94a3b8!important;
}
body:has(.dark-theme-marker) .panel,
body:has(.dark-theme-marker) .metric-card,
body:has(.dark-theme-marker) .admin-summary-card,
body:has(.dark-theme-marker) .reader-table-card,
body:has(.dark-theme-marker) .reader-panel,
body:has(.dark-theme-marker) .reader-profile-box,
body:has(.dark-theme-marker) .book-card-shell,
body:has(.dark-theme-marker) .book-list-row,
body:has(.dark-theme-marker) .stat-card,
body:has(.dark-theme-marker) .cat-card,
body:has(.dark-theme-marker) .book-tile,
body:has(.dark-theme-marker) .staff-home-hero,
body:has(.dark-theme-marker) .home-metric,
body:has(.dark-theme-marker) .home-panel,
body:has(.dark-theme-marker) [data-testid="stMetric"]{
  background:#161b26!important;
  border-color:#272e3f!important;
  color:#e2e8f0!important;
}
body:has(.dark-theme-marker) .staff-home-hero .staff-home-title,
body:has(.dark-theme-marker) .home-panel-title{
  color:#f8fafc!important;
}
body:has(.dark-theme-marker) .staff-home-hero .staff-home-sub,
body:has(.dark-theme-marker) .home-metric-label,
body:has(.dark-theme-marker) .home-metric-note{
  color:#94a3b8!important;
}
body:has(.dark-theme-marker) .activity-row{
  border-bottom-color:#272e3f!important;
}
body:has(.dark-theme-marker) .activity-title{
  color:#f8fafc!important;
}
body:has(.dark-theme-marker) .activity-detail{
  color:#94a3b8!important;
}
body:has(.dark-theme-marker) [data-testid="stTextInput"] input,
body:has(.dark-theme-marker) [data-testid="stTextArea"] textarea,
body:has(.dark-theme-marker) [data-baseweb="select"]>div{
  background:#181d2c!important;
  color:#f1f5f9!important;
  border-color:#2d364c!important;
}
body:has(.dark-theme-marker) [data-testid="stDataFrame"]{
  background:#161b26!important;
  color:#e2e8f0!important;
}
body:has(.dark-theme-marker) .ai-answer-shell{
  background:#161b26!important;
  border-color:#272e3f!important;
  color:#e2e8f0!important;
}
body:has(.dark-theme-marker) .ai-fast-note,
body:has(.dark-theme-marker) .search-result-note{
  background:linear-gradient(135deg,#1e192c,#2b1d38)!important;
  border-color:#3d2b52!important;
  color:#d8b4fe!important;
}

@media(max-height:760px){
  section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]{padding-top:12px!important;margin-top:-48px!important;}
  section[data-testid="stSidebar"] .side-brand{padding-bottom:14px!important;margin-bottom:13px!important;}
  section[data-testid="stSidebar"] .profile-card{padding:13px 14px!important;min-height:82px!important;margin-bottom:11px!important;}
  section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll .stButton>button{min-height:49px!important;font-size:.88rem!important;}
  section[data-testid="stSidebar"] .side-group{padding-top:11px!important;}
}


/* ===== V28 SIDEBAR: reliable scrolling + bold labels ===== */
/* Scroll the sidebar content itself so mouse wheel/touchpad always works.
   Keep the top identity card and bottom tools sticky, like the reference. */
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]{
  position:relative!important;
  overflow-y:auto!important;
  overflow-x:hidden!important;
  overscroll-behavior:contain!important;
  scrollbar-width:thin!important;
  scrollbar-color:#c9ced9 transparent!important;
}
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]::-webkit-scrollbar{width:6px!important;}
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]::-webkit-scrollbar-track{background:transparent!important;}
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]::-webkit-scrollbar-thumb{background:#c9ced9!important;border-radius:999px!important;}
section[data-testid="stSidebar"] .st-key-sidebar_top_fixed{
  position:sticky!important;
  top:0!important;
  z-index:50!important;
  background:#fff!important;
  padding-top:2px!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll{
  flex:0 0 auto!important;
  min-height:auto!important;
  height:auto!important;
  max-height:none!important;
  overflow:visible!important;
  padding:0 5px 14px 0!important;
  margin:0!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed{
  position:sticky!important;
  bottom:0!important;
  z-index:60!important;
  background:#fff!important;
  padding-top:10px!important;
  padding-bottom:2px!important;
}
/* Make the menu look stronger, closer to the supplied reference. */
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll .stButton{
  margin:0 0 2px!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll .stButton>button{
  min-height:50px!important;
  padding:9px 14px!important;
  font-size:.95rem!important;
  font-weight:800!important;
  line-height:1.28!important;
  letter-spacing:-.05px!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll .stButton>button p,
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll .stButton>button span:not([data-testid="stIconMaterial"]){
  font-weight:800!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_core_group button[kind="primary"],
section[data-testid="stSidebar"] .st-key-sidebar_core_group button[data-testid="stBaseButton-primary"]{
  font-weight:950!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_ai_group button,
section[data-testid="stSidebar"] .st-key-sidebar_report_group button{
  font-weight:850!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_ai_group button p,
section[data-testid="stSidebar"] .st-key-sidebar_report_group button p{
  font-weight:850!important;
}
section[data-testid="stSidebar"] .side-group{
  padding:15px 13px 8px!important;
  font-size:.73rem!important;
  font-weight:1000!important;
  letter-spacing:1.45px!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed .stButton>button,
section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed button[kind="primary"],
section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed button[data-testid="stBaseButton-primary"]{
  font-weight:750!important;
}
/* Extra breathing room so the last report item never hides under the sticky tools. */
section[data-testid="stSidebar"] .st-key-sidebar_report_group{padding-bottom:10px!important;}




/* ===== V30 SIDEBAR: HOME + FIXED LOGOUT ===== */
/* Make the sidebar a true 3-part layout: fixed header, scrollable menu, fixed tools. */
section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]{
  display:flex!important;
  flex-direction:column!important;
  height:calc(100vh + 48px)!important;
  min-height:0!important;
  overflow:hidden!important;
  padding:18px 26px 10px 27px!important;
  margin-top:-48px!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_top_fixed{
  position:relative!important;
  top:auto!important;
  flex:0 0 auto!important;
  z-index:5!important;
  background:#fff!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll{
  position:relative!important;
  flex:1 1 auto!important;
  min-height:0!important;
  height:auto!important;
  max-height:none!important;
  overflow-y:auto!important;
  overflow-x:hidden!important;
  overscroll-behavior:contain!important;
  padding:0 6px 12px 0!important;
  margin:0 -3px 0 0!important;
  scrollbar-width:thin!important;
  scrollbar-color:#c9ced9 transparent!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll::-webkit-scrollbar{width:5px!important;}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll::-webkit-scrollbar-track{background:transparent!important;}
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll::-webkit-scrollbar-thumb{background:#c9ced9!important;border-radius:999px!important;}
section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed{
  position:relative!important;
  bottom:auto!important;
  flex:0 0 auto!important;
  z-index:10!important;
  background:#fff!important;
  border-top:1px solid #ececf1!important;
  padding:10px 0 0!important;
  margin:0!important;
}
/* Home appears as its own button above the management heading. */
section[data-testid="stSidebar"] .st-key-sidebar_home_group [data-testid="stVerticalBlock"]{gap:0!important;}
section[data-testid="stSidebar"] .st-key-sidebar_home_group .stButton{margin:0 0 6px!important;}
section[data-testid="stSidebar"] .st-key-sidebar_home_group .stButton>button{
  width:100%!important;
  min-height:48px!important;
  padding:9px 14px!important;
  border:1px solid #ececf4!important;
  border-radius:11px!important;
  background:#fff!important;
  color:#31425d!important;
  justify-content:flex-start!important;
  text-align:left!important;
  gap:10px!important;
  font-size:.95rem!important;
  font-weight:850!important;
  box-shadow:none!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_home_group .stButton>button [data-testid="stIconMaterial"]{
  color:#3d536d!important;
  font-size:1.35rem!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_home_group button[kind="primary"],
section[data-testid="stSidebar"] .st-key-sidebar_home_group button[data-testid="stBaseButton-primary"]{
  background:linear-gradient(90deg,#625cf3,#8c5cf2)!important;
  color:#fff!important;
  border-color:transparent!important;
  box-shadow:0 7px 16px rgba(91,87,219,.14)!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_home_group button[kind="primary"] *,
section[data-testid="stSidebar"] .st-key-sidebar_home_group button[data-testid="stBaseButton-primary"] *{color:#fff!important;}
/* Stronger menu labels, including AI/Report. */
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll .stButton>button,
section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll .stButton>button p{
  font-weight:850!important;
}
section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed .stButton>button,
section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed .stButton>button p{
  font-weight:800!important;
}
/* Keep both bottom buttons fully visible even on shorter screens. */
@media(max-height:760px){
  section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed .stButton>button{min-height:43px!important;}
  section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed .stButton{margin-bottom:6px!important;}
  section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll .stButton>button{min-height:46px!important;}
  section[data-testid="stSidebar"] .side-group{padding-top:10px!important;padding-bottom:6px!important;}
}

/* ===== V29 COMPACT BOOK DIALOG ===== */
div[data-baseweb="modal"]:has(.book-dialog-marker){
    align-items:center!important;
    justify-content:center!important;
    padding:18px!important;
}
div[data-baseweb="modal"]:has(.book-dialog-marker)>div{
    margin:0!important;
    align-self:center!important;
}
div[data-testid="stDialog"]:has(.book-dialog-marker){
    align-items:center!important;
    justify-content:center!important;
}
div[data-testid="stDialog"] div[role="dialog"]:has(.book-dialog-marker){
    position:relative!important;
    inset:auto!important;
    right:auto!important;bottom:auto!important;left:auto!important;top:auto!important;
    transform:none!important;
    margin:0!important;
    width:min(760px,calc(100vw - 36px))!important;
    max-width:760px!important;
    max-height:86vh!important;
    overflow-y:auto!important;
    background:#ffffff!important;
    color:#252b40!important;
    border:1px solid #e5e0ef!important;
    border-radius:20px!important;
    box-shadow:0 24px 65px rgba(67,48,116,.20)!important;
}
div[role="dialog"]:has(.book-dialog-marker) [data-testid="stMarkdownContainer"] p,
div[role="dialog"]:has(.book-dialog-marker) [data-testid="stMarkdownContainer"] li,
div[role="dialog"]:has(.book-dialog-marker) label{color:#32384c!important;}
div[role="dialog"]:has(.book-dialog-marker) input,
div[role="dialog"]:has(.book-dialog-marker) textarea,
div[role="dialog"]:has(.book-dialog-marker) [data-baseweb="input"]>div,
div[role="dialog"]:has(.book-dialog-marker) [data-baseweb="textarea"]{
    background:#fff!important;
    color:#2f3448!important;
    border-color:#ded9e8!important;
}
div[role="dialog"]:has(.book-dialog-marker) [data-testid="stButton"] button,
div[role="dialog"]:has(.book-dialog-marker) [data-testid="stFormSubmitButton"] button{
    min-height:44px!important;
    border-radius:12px!important;
}
div[role="dialog"]:has(.book-dialog-marker) [data-testid="stFormSubmitButton"] button[kind="primary"]{
    background:linear-gradient(90deg,#6b5cf2,#8c52ed,#d942b7)!important;
    color:#fff!important;
    border:0!important;
}
@media(max-width:780px){
  div[data-testid="stDialog"] div[role="dialog"]:has(.book-dialog-marker){
    width:calc(100vw - 18px)!important;max-width:none!important;max-height:90vh!important;border-radius:16px!important;
  }
}
</style>
''', unsafe_allow_html=True)

if st.session_state.ui_theme=='dark':
    st.markdown('<span class="dark-theme-marker"></span>',unsafe_allow_html=True)

# ------------------------------------------------------------------
# HELPERS
# ------------------------------------------------------------------
def static_url(relative_path):
    rel=str(relative_path or '').replace('\\','/').lstrip('/')
    return f'app/static/{rel}'


def get_ai_service():
    # Reuse the Gemini client/policy chunks within this browser session.
    if '_ai_service' not in st.session_state:
        st.session_state._ai_service=AIService()
    return st.session_state._ai_service


def money(v):
    return f'{int(v or 0):,} VNĐ'.replace(',', '.')


def role_name(role):
    return {'admin':'Quản trị viên','librarian':'Thủ thư','reader':'Độc giả'}.get(role, role)


def status_vi(s):
    return {
        'pending':'Chờ duyệt','borrowed':'Đang mượn','overdue':'Quá hạn',
        'return_requested':'Chờ xác nhận trả','returned':'Đã trả','rejected':'Từ chối',
        'fulfilled':'Đã xử lý','cancelled':'Đã hủy','active':'Hoạt động','locked':'Bị khóa',
        'paid':'Đã thanh toán','unpaid':'Chưa thanh toán','lost':'Chưa trả / Mất','lost_resolved':'Đã xử lý mất sách'
    }.get(s,s)


def cover(book):
    p=STATIC_DIR/(book.get('cover_image') or '')
    return p if p.exists() else None


def csv_bytes(rows):
    return pd.DataFrame(rows).to_csv(index=False).encode('utf-8-sig') if rows else b''


def page_head(title, sub=''):
    st.markdown(f'<div class="page-title">{html.escape(title)}</div><div class="page-sub">{html.escape(sub)}</div>', unsafe_allow_html=True)


if 'user' not in st.session_state: st.session_state.user=None
if 'public_page' not in st.session_state: st.session_state.public_page='home'
if 'nav_page' not in st.session_state: st.session_state.nav_page=None
if 'chat_messages' not in st.session_state: st.session_state.chat_messages=[{'role':'assistant','content':'Xin chào! Mình là Trợ lý SmartLibrary AI. Bạn muốn tìm sách hay hỏi kiến thức gì?'}]
if 'selected_book' not in st.session_state: st.session_state.selected_book=None
if 'login_user' not in st.session_state: st.session_state.login_user=''
if 'login_pass' not in st.session_state: st.session_state.login_pass=''
if 'login_mode' not in st.session_state: st.session_state.login_mode='login'
if 'public_category' not in st.session_state: st.session_state.public_category='Tất cả'
if 'public_catalog_page' not in st.session_state: st.session_state.public_catalog_page=0
if 'public_catalog_signature' not in st.session_state: st.session_state.public_catalog_signature=None
if st.session_state.get('_public_chat_version')!='v16':
    st.session_state._public_chat_version='v16'
    st.session_state.public_chat_messages=[{'role':'assistant','content':'Xin chào! Mình là Trợ lý AI LIBRA. Bạn muốn tìm sách, hỏi quy định thư viện hay hỏi kiến thức gì?'}]
elif 'public_chat_messages' not in st.session_state:
    st.session_state.public_chat_messages=[{'role':'assistant','content':'Xin chào! Mình là Trợ lý AI LIBRA. Bạn muốn tìm sách, hỏi quy định thư viện hay hỏi kiến thức gì?'}]
# public_chat query param is treated as a one-shot open event (V16)

# ------------------------------------------------------------------
# PUBLIC LOBBY
# ------------------------------------------------------------------
def public_nav():
    st.markdown('<div class="public-top-strip">LIBRA&nbsp;&nbsp;✦&nbsp;&nbsp;THƯ VIỆN THÔNG MINH&nbsp;&nbsp;✦&nbsp;&nbsp;TRỢ LÝ AI & BÁO CÁO DỮ LIỆU SỐ</div>',unsafe_allow_html=True)
    st.markdown('<div class="public-nav">',unsafe_allow_html=True)
    cols=st.columns([1.3,.65,.75,.62,.65,.65,.9,1.25,.68,.68])
    with cols[0]: st.markdown('<div class="public-logo">LIBRA <small>VN</small></div>',unsafe_allow_html=True)
    category_map=[('Tin học','Công nghệ thông tin'),('Trinh thám','Trinh thám'),('Triết lý','Kỹ năng sống'),('Kỹ năng','Kỹ năng sống'),('Văn học','Văn học Việt Nam')]
    for idx,(label,category) in enumerate(category_map,1):
        with cols[idx]:
            if st.button(label,key='pubnav_'+label,use_container_width=True):
                st.session_state.public_category=category; st.session_state.public_catalog_page=0; st.session_state.public_page='catalog'; st.rerun()
    with cols[6]:
        if st.button('🤖 Trợ lý AI',key='pubnav_ai',use_container_width=True):
            st.query_params['public_chat']='1'; st.rerun()
    with cols[7]:
        if st.button('📄 Báo cáo & Xuất file',key='pubnav_reports',use_container_width=True):
            st.session_state.login_mode='login'; st.session_state.public_page='login'; st.rerun()
    with cols[8]:
        st.markdown('<div class="nav-action">',unsafe_allow_html=True)
        if st.button('Đăng ký',key='pubnav_register',use_container_width=True):
            st.session_state.login_mode='register'; st.session_state.public_page='login'; st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
    with cols[9]:
        st.markdown('<div class="nav-login">',unsafe_allow_html=True)
        if st.button('Đăng nhập',key='pubnav_login',type='primary',use_container_width=True):
            st.session_state.login_mode='login'; st.session_state.public_page='login'; st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
    st.markdown('</div>',unsafe_allow_html=True)

def book_tile(book, key, allow_detail=True):
    cp=cover(book)
    if cp:
        src=static_url(book.get('cover_image'))
        visual=(
            f'<img class="book-cover-img" src="{src}" '
            f'alt="{html.escape(book.get("title","Sách"))}" '
            f'loading="lazy" decoding="async">'
        )
    else:
        visual='<div class="book-cover-empty">📖</div>'
    card=(
        '<div class="book-tile">' + visual +
        f'<div class="book-name">{html.escape(book["title"])}</div>' +
        f'<div class="book-meta">{html.escape(book.get("author", ""))}<br>Còn {book.get("available",0)}/{book.get("quantity",0)} bản</div>' +
        f'<span class="badge">{html.escape(book.get("category", "Khác"))}</span>' +
        '</div>'
    )
    st.markdown(card,unsafe_allow_html=True)
    if allow_detail and st.button('Xem chi tiết',key=key,use_container_width=True):
        db.increment_book_view(book['id'])
        st.session_state.selected_book=book['id']
        st.rerun()


def render_public_detail():
    bid=st.session_state.selected_book
    if not bid: return
    book=db.get_book(bid)
    if not book: return
    st.divider(); page_head('Chi tiết sách', 'Thông tin đầu sách trong kho')
    a,b=st.columns([1,2.4],gap='large')
    with a:
        cp=cover(book)
        if cp: st.image(str(cp),use_container_width=True)
    with b:
        st.subheader(book['title']); st.caption(f"{book['id']} • {book['author']}")
        st.write(f"**Thể loại:** {book['category']}")
        st.write(f"**Năm xuất bản:** {book.get('year') or '—'}")
        st.write(f"**Vị trí:** {book.get('location') or '—'}")
        st.write(f"**Tình trạng:** còn {book['available']}/{book['quantity']} bản")
        st.write(book.get('description') or 'Chưa có mô tả.')
        if st.button('Đăng nhập để mượn sách',type='primary'):
            st.session_state.public_page='login'; st.rerun()
    if st.button('Đóng chi tiết'):
        st.session_state.selected_book=None; st.rerun()


def public_home():
    stats,cats,_=db.admin_stats()
    tech=static_url(LOBBY_HERO); detective=static_url(LOBBY_DETECTIVE); philosophy=static_url(LOBBY_PHILOSOPHY)
    st.markdown(f'''<div class="hero-carousel">
      <div class="hero-slide s1" style="background-image:url('{tech}')"><div class="hero-copy"><div class="hero-chip">💻 SÁCH TIN HỌC & CÔNG NGHỆ</div><h1>Học công nghệ<br>từ những cuốn sách hay</h1><p>Python, AI, dữ liệu, mạng máy tính và kỹ năng lập trình được chọn lọc cho sinh viên.</p></div></div>
      <div class="hero-slide s2" style="background-image:url('{detective}')"><div class="hero-copy"><div class="hero-chip">🔎 TRINH THÁM & BÍ ẨN</div><h1>Lần theo manh mối<br>qua từng trang sách</h1><p>Những vụ án, bí ẩn và câu chuyện phá án hấp dẫn dành cho người thích suy luận.</p></div></div>
      <div class="hero-slide s3" style="background-image:url('{philosophy}')"><div class="hero-copy"><div class="hero-chip">🌿 TRIẾT LÝ & PHÁT TRIỂN BẢN THÂN</div><h1>Đọc để hiểu mình<br>và sống sâu sắc hơn</h1><p>Những cuốn sách giúp mở rộng góc nhìn, rèn tư duy và xây dựng một cuộc sống có ý nghĩa.</p></div></div>
    </div>''',unsafe_allow_html=True)
    st.markdown('<div class="hero-search-panel">',unsafe_allow_html=True)
    a,b=st.columns([4.5,1])
    with a: q=st.text_input('Tìm nhanh ở sảnh',placeholder='🔎 Tìm sách, tác giả, thể loại...',label_visibility='collapsed',key='lobby_search')
    with b:
        if st.button('Tìm kiếm',type='primary',use_container_width=True,key='lobby_search_btn'):
            st.session_state.public_category='Tất cả'; st.session_state.public_catalog_page=0; st.session_state.public_page='catalog'; st.session_state.quick_search=q; st.rerun()
    st.markdown('</div>',unsafe_allow_html=True)
    st.markdown('<div class="public-content-pad">',unsafe_allow_html=True)
    st.markdown('<div class="public-section-title">Thư viện trong những con số</div><div class="public-section-sub">Dữ liệu được cập nhật trực tiếp từ hệ thống</div>',unsafe_allow_html=True)
    availability=round((stats['available']/stats['copies']*100),1) if stats['copies'] else 0
    cols=st.columns(4); vals=[('📚',stats['titles'],'Đầu sách'),('👥',stats['readers'],'Độc giả hoạt động'),('📖',stats['borrowed'],'Đang được mượn'),('✨',f'{availability}%','Tỷ lệ bản sẵn sàng')]
    for col,(ico,num,label) in zip(cols,vals):
        with col: st.markdown(f'<div class="stat-card"><div class="stat-icon">{ico}</div><div class="stat-num">{num}</div><div class="stat-label">{label}</div></div>',unsafe_allow_html=True)
    st.markdown('<div class="public-section-title">Khám phá theo thể loại</div><div class="public-section-sub">Tìm đúng cuốn sách bạn đang cần</div>',unsafe_allow_html=True)
    icons=['💻','🕵️','🌱','📖','🧠','💼','🔬','🎨']; cols=st.columns(4)
    for i,c in enumerate(cats[:8]):
        with cols[i%4]: st.markdown(f'<div class="cat-card"><div class="cat-icon">{icons[i%len(icons)]}</div><div class="cat-title">{html.escape(c["category"])}</div><div class="cat-count">{c["titles"]} đầu sách</div></div>',unsafe_allow_html=True)
    st.markdown('<div class="public-section-title">Sách được quan tâm</div><div class="public-section-sub">Các đầu sách nổi bật trong thư viện</div>',unsafe_allow_html=True)
    preferred_ids=['U021','U007','U011','U016','U001']
    books=[db.get_book(bid) for bid in preferred_ids]
    books=[bk for bk in books if bk]
    if len(books)<5:
        used={x['id'] for x in books}
        extras=[bk for bk in db.list_books() if 'assets/user_covers/' in (bk.get('cover_image') or '') and bk['id'] not in used]
        books=(books+extras)[:5]
    cols=st.columns(5)
    for i,(col,bk) in enumerate(zip(cols,books)):
        with col: book_tile(bk,f'pubtop_{i}_{bk["id"]}')
    render_public_detail(); st.markdown('</div>',unsafe_allow_html=True)

def public_catalog():
    st.markdown('<div class="public-content-pad">',unsafe_allow_html=True)
    page_head('Tra cứu sách thông minh','Tìm theo tên sách, tác giả, mã sách, ISBN hoặc chủ đề — kết quả xếp theo độ liên quan BM25 từ MySQL')

    all_books=db.list_books()
    copies=sum(int(x.get('quantity') or 0) for x in all_books)
    available=sum(int(x.get('available') or 0) for x in all_books)
    categories=len({x.get('category') for x in all_books if x.get('category')})
    s1,s2,s3,s4=st.columns(4)
    for col,(ico,label,value,note) in zip(
        (s1,s2,s3,s4),
        [
            ('📚','Đầu sách',len(all_books),f'{copies} bản trong kho'),
            ('✅','Bản sẵn sàng',available,'Có thể mượn ngay'),
            ('🏷️','Thể loại',categories,'Danh mục đang phục vụ'),
            ('🤖','Tìm kiếm','BM25 + AI','Dữ liệu trực tiếp từ MySQL'),
        ]
    ):
        with col:
            st.markdown(f'<div class="admin-summary-card"><div class="admin-summary-label">{ico} {label}</div><div class="admin-summary-value">{value}</div><div class="admin-summary-note">{note}</div></div>',unsafe_allow_html=True)

    if 'catalog_search_q' not in st.session_state:
        st.session_state.catalog_search_q=''
    if 'catalog_search_cat' not in st.session_state:
        st.session_state.catalog_search_cat=st.session_state.public_category
    if 'catalog_search_only' not in st.session_state:
        st.session_state.catalog_search_only=False

    incoming=st.session_state.pop('quick_search','') if 'quick_search' in st.session_state else ''
    if incoming:
        st.session_state.catalog_search_q=incoming
        st.session_state.public_catalog_page=0

    st.write('')
    with st.form('public_catalog_search_form'):
        a,b,c,d=st.columns([2.5,1.1,.85,.7])
        with a:
            q_input=st.text_input('Từ khóa',value=st.session_state.catalog_search_q,placeholder='Ví dụ: Python, tình yêu, trinh thám, Nguyễn Nhật Ánh, B001...')
        cats=['Tất cả']+db.list_categories()
        selected=st.session_state.public_category if st.session_state.public_category in cats else 'Tất cả'
        with b:
            cat_input=st.selectbox('Thể loại',cats,index=cats.index(selected))
        with c:
            only_input=st.checkbox('Chỉ sách còn',value=st.session_state.catalog_search_only)
        with d:
            st.markdown('<div style="height:28px"></div>',unsafe_allow_html=True)
            submitted=st.form_submit_button('🔎 Tra cứu',type='primary',use_container_width=True)
    if submitted:
        st.session_state.catalog_search_q=q_input.strip()
        st.session_state.catalog_search_cat=cat_input
        st.session_state.catalog_search_only=bool(only_input)
        st.session_state.public_category=cat_input
        st.session_state.public_catalog_page=0
        st.rerun()

    q=st.session_state.catalog_search_q.strip()
    cat=st.session_state.catalog_search_cat if st.session_state.catalog_search_cat in ['Tất cả']+db.list_categories() else 'Tất cả'
    only=st.session_state.catalog_search_only
    books=db.list_books(q,cat,only)

    # IMPORTANT: BM25 already returns relevance order. Never sort it again when searching.
    if not q:
        books=sorted(books,key=lambda bk:(0 if 'assets/user_covers/' in (bk.get('cover_image') or '') else 1,bk.get('title','').lower()))

    if q:
        st.markdown(
            f'<div class="search-result-note"><b>🎯 {len(books)} kết quả phù hợp</b> cho “{html.escape(q)}”. '
            'Thứ tự dựa trên mức độ liên quan, không phải thứ tự ABC.</div>',
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<div class="search-result-note"><b>📚 Kho sách</b> — nhập từ khóa để tìm thông minh theo nội dung.</div>',unsafe_allow_html=True)

    if not books:
        st.info('Không tìm thấy sách phù hợp. Hãy thử tên tác giả, thể loại hoặc từ khóa ngắn hơn.')
        st.markdown('</div>',unsafe_allow_html=True)
        return

    page_size=8
    total_pages=max(1, math.ceil(len(books)/page_size))
    st.session_state.public_catalog_page=min(st.session_state.public_catalog_page,total_pages-1)
    page=st.session_state.public_catalog_page
    start_idx=page*page_size
    shown=books[start_idx:start_idx+page_size]

    p1,p2,p3=st.columns([1,2,1])
    with p1:
        if st.button('← Trang trước',disabled=page<=0,use_container_width=True,key='catalog_prev'):
            st.session_state.public_catalog_page=max(0,page-1); st.rerun()
    with p2:
        st.markdown(f'<div style="text-align:center;padding:10px;color:#7c8498;font-weight:850">Trang {page+1}/{total_pages} • {len(books)} kết quả</div>',unsafe_allow_html=True)
    with p3:
        if st.button('Trang sau →',disabled=page>=total_pages-1,use_container_width=True,key='catalog_next'):
            st.session_state.public_catalog_page=min(total_pages-1,page+1); st.rerun()

    for i in range(0,len(shown),4):
        cols=st.columns(4,gap='medium')
        for j,bk in enumerate(shown[i:i+4]):
            with cols[j]:
                book_tile(bk,f'pubcat_{page}_{bk["id"]}')
                if q and bk.get('_bm25_score') is not None:
                    st.caption(f'🎯 Độ liên quan: {bk["_bm25_score"]:.2f}')

    render_public_detail()
    st.markdown('</div>',unsafe_allow_html=True)


def public_about():
    page_head('Giới thiệu SmartLibrary AI','Hệ thống quản lý thư viện tích hợp trí tuệ nhân tạo')
    a,b,c=st.columns(3)
    for col,ico,title,text in [
        (a,'📚','Quản lý tập trung','Quản lý sách, độc giả, mượn trả, đặt trước và tiền phạt trên một hệ thống.'),
        (b,'🤖','Trợ lý AI','Hỗ trợ tra cứu sách, gợi ý tài liệu và trả lời kiến thức tổng quát.'),
        (c,'📊','Báo cáo trực quan','Theo dõi tình hình vận hành và xuất dữ liệu nhanh cho quản trị viên.')]:
        with col: st.markdown(f'<div class="panel" style="min-height:170px"><div style="font-size:2rem">{ico}</div><h3>{title}</h3><div class="page-sub">{text}</div></div>',unsafe_allow_html=True)


def public_contact():
    page_head('Liên hệ thư viện','Thông tin hỗ trợ độc giả')
    a,b=st.columns(2)
    with a:
        st.info(f"📧 {db.get_setting('library_email','library@ictu.edu.vn')}\n\n☎️ {db.get_setting('library_phone','0966320627')}\n\n📍 Trung tâm Thư viện - SmartLibrary")
    with b:
        with st.form('contact_form'):
            st.text_input('Họ tên'); st.text_input('Email'); st.text_area('Nội dung')
            if st.form_submit_button('Gửi phản hồi',type='primary'): st.success('Đã ghi nhận phản hồi (bản demo).')


def login_page():
    left,center,right=st.columns([1.15,1,1.15])
    with center:
        st.markdown('<div class="login-page-wrap">',unsafe_allow_html=True)
        st.markdown('<div class="login-brand"><div class="login-logo">▣</div><div class="login-title">SmartLibrary <span class="ai-badge">AI</span></div><div class="login-sub">Hệ thống Quản lý Thư viện Thông minh</div></div>',unsafe_allow_html=True)
        ta,tb=st.columns(2)
        with ta:
            if st.button('Đăng nhập',type='primary' if st.session_state.login_mode=='login' else 'secondary',use_container_width=True,key='switch_login'): st.session_state.login_mode='login';st.rerun()
        with tb:
            if st.button('Đăng ký độc giả',type='primary' if st.session_state.login_mode=='register' else 'secondary',use_container_width=True,key='switch_register'): st.session_state.login_mode='register';st.rerun()
        if st.session_state.login_mode=='login':
            with st.container(border=True):
                st.markdown('<div class="login-mode-title">Đăng nhập</div><div class="login-mode-sub">Đăng nhập để sử dụng hệ thống thư viện</div>',unsafe_allow_html=True)
                with st.form('login_form'):
                    u=st.text_input('👤 Tên đăng nhập',value=st.session_state.login_user,placeholder='Tên đăng nhập...')
                    p=st.text_input('🔒 Mật khẩu',value=st.session_state.login_pass,type='password',placeholder='Mật khẩu...')
                    go=st.form_submit_button('↪ Đăng nhập',type='primary',use_container_width=True)
                if go:
                    ok,msg,user=auth.authenticate(u,p)
                    if ok:
                        st.session_state.user=user;st.session_state.nav_page='Trang chủ';db.log_activity(user['id'],'Đăng nhập','Đăng nhập hệ thống');st.query_params.clear();st.rerun()
                    st.error(msg)
                st.divider();st.markdown('<div class="quick-title">🔑 Tài khoản dùng thử nhanh</div>',unsafe_allow_html=True)
                x,y,z=st.columns(3)
                with x:
                    if st.button('Admin',use_container_width=True,key='quick_admin'): st.session_state.login_user='admin';st.session_state.login_pass='admin123';st.rerun()
                with y:
                    if st.button('Thủ thư',use_container_width=True,key='quick_librarian'): st.session_state.login_user='thuthu';st.session_state.login_pass='thuthu123';st.rerun()
                with z:
                    if st.button('Độc giả',use_container_width=True,key='quick_reader'): st.session_state.login_user='docgia';st.session_state.login_pass='reader123';st.rerun()
        else:
            with st.container(border=True):
                st.markdown('<div class="login-mode-title">Tạo tài khoản độc giả</div><div class="login-mode-sub">Đăng ký để mượn sách, đặt trước và sử dụng AI</div>',unsafe_allow_html=True)
                with st.form('register_form'):
                    full_name=st.text_input('Họ và tên');username=st.text_input('Tên đăng nhập');email=st.text_input('Email');phone=st.text_input('Số điện thoại');password=st.text_input('Mật khẩu',type='password');password2=st.text_input('Nhập lại mật khẩu',type='password');reg=st.form_submit_button('Tạo tài khoản',type='primary',use_container_width=True)
                if reg:
                    if password!=password2: st.error('Mật khẩu nhập lại không khớp.')
                    else:
                        ok,msg=auth.register_reader(username,password,full_name,email,phone)
                        if ok: st.success('Đăng ký thành công. Bạn có thể đăng nhập ngay.');st.session_state.login_user=username;st.session_state.login_pass=password;st.session_state.login_mode='login'
                        else: st.error(msg)
        if st.button('← Quay lại sảnh thư viện',use_container_width=True,key='back_lobby'): st.session_state.public_page='home';st.session_state.login_mode='login';st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)


def public_ai():
    st.markdown('<div class="public-content-pad">',unsafe_allow_html=True)
    page_head('Trợ lý AI thư viện','Hỏi về sách trong kho hoặc kiến thức tổng quát')
    ai=get_ai_service(); a,b,c=st.columns([1,2.4,1])
    with b:
        with st.container(border=True):
            for m in st.session_state.public_chat_messages:
                with st.chat_message(m['role']): st.markdown(m['content'])
            q=st.chat_input('Hỏi về sách, học tập, lập trình...',key='public_ai_input')
            if q:
                st.session_state.public_chat_messages.append({'role':'user','content':q})
                with st.chat_message("user"):
                    st.markdown(q)
                with st.chat_message("assistant"):
                    ans=st.write_stream(ai.answer_stream(q,st.session_state.public_chat_messages[:-1]))
                st.session_state.public_chat_messages.append({'role':'assistant','content':ans})
                st.rerun()
            if st.button('← Quay lại trang chủ',use_container_width=True,key='public_ai_back'): st.query_params.clear(); st.session_state.public_page='home'; st.rerun()
    st.markdown('</div>',unsafe_allow_html=True)

@st.dialog("Trợ lý ảo LIBRA", width="small")
def public_chat_dialog():
    ai=get_ai_service()
    ai_state='🟢 Gemini AI' if ai.enabled else '🟡 Local RAG'
    st.markdown(
        f'<div class="waka-head-bar">'
        f'<div class="waka-head-title"><span class="waka-bot-avatar">🤖</span> <b>Trợ lý ảo LIBRA</b> <span class="waka-status-badge">{ai_state}</span></div>'
        f'</div>',
        unsafe_allow_html=True
    )
    if len(st.session_state.public_chat_messages)<=1:
        st.markdown('<div class="waka-suggest-prompt">Bạn có muốn LIBRA gợi ý sách theo sở thích không?</div>',unsafe_allow_html=True)
        suggestions=[
            '📖 Gợi ý sách theo sở thích',
            '🔥 Sách mượn nhiều nhất',
            '📋 Hướng dẫn mượn / trả',
            '💡 Giải thích RAG & BM25'
        ]
        cols=st.columns(2)
        for i,prompt in enumerate(suggestions):
            with cols[i%2]:
                if st.button(prompt,key=f'popup_suggest_{i}',use_container_width=True):
                    st.session_state.public_chat_messages.append({'role':'user','content':prompt})
                    st.rerun(scope='fragment')

    if len(st.session_state.public_chat_messages)>1:
        for m in st.session_state.public_chat_messages[-6:]:
            if m['role']=='user':
                st.markdown(f'<div class="waka-msg-user">{html.escape(m["content"])}</div>',unsafe_allow_html=True)
            else:
                st.markdown('<div class="waka-msg-ai-wrap"><div class="waka-ai-avatar">🤖</div><div class="waka-msg-ai-box">',unsafe_allow_html=True)
                st.markdown(m['content'])
                st.markdown('</div></div>',unsafe_allow_html=True)

    if st.session_state.public_chat_messages and st.session_state.public_chat_messages[-1]['role']=='user':
        last_user_q=st.session_state.public_chat_messages[-1]['content']
        rag=ai.retrieve(last_user_q)
        st.markdown('<div class="waka-msg-ai-wrap"><div class="waka-ai-avatar">🤖</div><div class="waka-msg-ai-box">',unsafe_allow_html=True)
        answer=st.write_stream(ai.answer_stream(last_user_q,st.session_state.public_chat_messages[:-1],rag=rag))
        st.markdown('</div></div>',unsafe_allow_html=True)
        st.session_state.public_chat_messages.append({'role':'assistant','content':answer})
        st.rerun(scope='fragment')

    with st.form('waka_chat_form',clear_on_submit=True):
        q=st.text_input('Nhập tin nhắn',placeholder='Nhập tin nhắn...',label_visibility='collapsed')
        send=st.form_submit_button('✈ Gửi',type='primary',use_container_width=True)
    if send and q.strip():
        st.session_state.public_chat_messages.append({'role':'user','content':q.strip()})
        st.rerun(scope='fragment')

    c1,c2=st.columns(2)
    with c1:
        if st.button('🔄 Xóa hội thoại',key='clear_public_chat',use_container_width=True):
            st.session_state.public_chat_messages=[{'role':'assistant','content':'Xin chào! Bạn muốn tìm sách hay hỏi điều gì?'}]
            st.rerun(scope='fragment')
    with c2:
        if st.button('✕ Đóng',key='close_public_chat',use_container_width=True):
            st.rerun()




def public_footer():
    st.markdown('''<div class="public-footer"><div class="footer-grid"><div><div class="footer-brand">LIBRA</div><div class="footer-small">Thư viện Thông minh tích hợp quản lý sách, mượn trả, thống kê và trợ lý AI.</div><div class="footer-small" style="margin-top:12px">☎ 0966320627<br>✉ library@ictu.edu.vn</div></div><div><div class="footer-head">Về thư viện</div><div class="footer-link">Giới thiệu</div><div class="footer-link">Kho sách</div><div class="footer-link">Thể loại</div><div class="footer-link">Liên hệ</div></div><div><div class="footer-head">Thông tin hữu ích</div><div class="footer-link">Quy định mượn trả</div><div class="footer-link">Chính sách tiền phạt</div><div class="footer-link">Câu hỏi thường gặp</div><div class="footer-link">Bảo mật thông tin</div></div><div><div class="footer-head">Hỗ trợ</div><div class="footer-link">Trợ lý AI</div><div class="footer-link">Hướng dẫn sử dụng</div><div class="footer-link">Phản hồi</div><div class="footer-link">Thông báo</div></div></div><div class="footer-small" style="margin-top:25px;padding-top:18px;border-top:1px solid #493454">© 2026 LIBRA • Hệ thống Quản lý Thư viện Thông minh</div></div>''',unsafe_allow_html=True)

def render_public():
    st.markdown('<div class="public-shell">',unsafe_allow_html=True)
    public_nav()
    if st.session_state.public_page=='home': public_home()
    elif st.session_state.public_page=='catalog': public_catalog()
    elif st.session_state.public_page=='about': st.markdown('<div class="public-content-pad">',unsafe_allow_html=True); public_about(); st.markdown('</div>',unsafe_allow_html=True)
    elif st.session_state.public_page=='contact': st.markdown('<div class="public-content-pad">',unsafe_allow_html=True); public_contact(); st.markdown('</div>',unsafe_allow_html=True)
    elif st.session_state.public_page=='login': login_page()
    public_footer()
    st.markdown('<a class="floating-ai" href="?public_chat=1" target="_self" title="Mở trợ lý AI"><span class="chat-glyph"></span></a>',unsafe_allow_html=True)
    # One-shot: clear the URL flag immediately so later clicks/reruns do NOT reopen chat.
    if st.query_params.get('public_chat') == '1':
        st.query_params.clear()
        public_chat_dialog()
    st.markdown('</div>',unsafe_allow_html=True)

# ------------------------------------------------------------------
# LOGGED-IN SIDEBAR / HEADER
# ------------------------------------------------------------------
ADMIN_MENU=[
    'Trang chủ','Tổng quan & Thống kê','Tra cứu & Quản lý Sách','Quản lý Độc giả',
    'Quản lý Mượn / Trả / Phạt','Đặt trước Sách','Tài khoản & Phân quyền',
    'Trợ lý AI & Gợi ý Sách','Báo cáo & Xuất dữ liệu','Cài đặt'
]
LIBRARIAN_MENU=[
    'Trang chủ','Tổng quan & Thống kê','Tra cứu & Quản lý Sách','Quản lý Độc giả',
    'Quản lý Mượn / Trả / Phạt','Đặt trước Sách','Trợ lý AI & Gợi ý Sách',
    'Báo cáo & Xuất dữ liệu','Cài đặt'
]
READER_MENU=['Trang chủ Hội viên','Quản lý tài khoản','Tủ sách cá nhân','Quản lý đơn hàng','Thành tích','Lịch sử giao dịch','Hỗ trợ khách hàng','Trợ lý AI & Gợi ý']



def sidebar(user):
    st.markdown("""<style>
    section[data-testid="stSidebar"] > div:first-child {
      height: 100vh !important;
    }
    section[data-testid="stSidebar"] [data-testid="stSidebarUserContent"]{
      display: flex !important;
      flex-direction: column !important;
      height: 100vh !important;
      max-height: 100vh !important;
      overflow: hidden !important;
      padding: 10px 10px 8px 10px !important;
      box-sizing: border-box !important;
    }
    section[data-testid="stSidebar"] .st-key-sidebar_top_fixed{
      flex: 0 0 auto !important;
      position: relative !important;
      background: transparent !important;
    }
    section[data-testid="stSidebar"] .st-key-sidebar_menu_scroll{
      flex: 1 1 auto !important;
      max-height: calc(100vh - 330px) !important;
      overflow-y: auto !important;
      overflow-x: hidden !important;
      padding-right: 2px !important;
      padding-bottom: 10px !important;
      margin-bottom: 4px !important;
    }
    section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed{
      flex: 0 0 auto !important;
      position: relative !important;
      bottom: 0 !important;
      left: 0 !important;
      right: 0 !important;
      width: 100% !important;
      background: transparent !important;
      border-top: 1px solid #e2e8f0 !important;
      padding-top: 6px !important;
      padding-bottom: 4px !important;
      margin-top: auto !important;
      z-index: 100 !important;
    }
    section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed .stButton{
      margin: 0 0 3px !important;
    }
    section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed .stButton>button{
      min-height: 36px !important;
      border-radius: 9px !important;
      font-weight: 800 !important;
      font-size: 0.85rem !important;
      padding: 5px 10px !important;
      background: #f8fafc !important;
      border: 1px solid #e2e8f0 !important;
    }
    body:has(.dark-theme-marker) section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed{
      border-top-color: #334155 !important;
    }
    body:has(.dark-theme-marker) section[data-testid="stSidebar"] .st-key-sidebar_bottom_fixed .stButton>button{
      background: #1e293b !important;
      border-color: #334155 !important;
      color: #e2e8f0 !important;
    }
    </style>""", unsafe_allow_html=True)
    if user['role']=='admin':
        core=['Trang chủ','Tổng quan & Thống kê','Tra cứu & Quản lý Sách','Quản lý Độc giả','Quản lý Mượn / Trả / Phạt','Đặt trước Sách','Tài khoản & Phân quyền']
        ai_items=['Trợ lý AI & Gợi ý Sách']
        report_items=['Báo cáo & Xuất dữ liệu']
    elif user['role']=='librarian':
        core=['Trang chủ','Tổng quan & Thống kê','Tra cứu & Quản lý Sách','Quản lý Độc giả','Quản lý Mượn / Trả / Phạt','Đặt trước Sách']
        ai_items=['Trợ lý AI & Gợi ý Sách']
        report_items=['Báo cáo & Xuất dữ liệu']
    else:
        core=['Trang chủ Hội viên','Quản lý tài khoản','Tủ sách cá nhân','Quản lý đơn hàng','Thành tích','Lịch sử giao dịch','Hỗ trợ khách hàng']
        ai_items=['Trợ lý AI & Gợi ý']
        report_items=[]

    all_items=core+ai_items+report_items
    default_item=core[1] if user['role'] in ('admin','librarian') and len(core)>1 else core[0]
    if st.session_state.nav_page not in all_items:
        st.session_state.nav_page=default_item

    labels={
        'Trang chủ':'Trang chủ',
        'Tổng quan & Thống kê':'Tổng quan & Thống kê',
        'Tra cứu & Quản lý Sách':'Tra cứu & Quản lý Sách',
        'Quản lý Độc giả':'Quản lý Độc giả',
        'Quản lý Mượn / Trả / Phạt':'Quản lý Mượn / Trả / Phạt',
        'Đặt trước Sách':'Đặt trước Sách',
        'Tài khoản & Phân quyền':'Quản lý Tài khoản & Phân quyền',
        'Trợ lý AI & Gợi ý Sách':'Trợ lý AI & Gợi ý Sách',
        'Báo cáo & Xuất dữ liệu':'Báo cáo & Xuất file Excel/CSV',
        'Trang chủ Hội viên':'Trang chủ Hội viên',
        'Quản lý tài khoản':'Quản lý tài khoản',
        'Tủ sách cá nhân':'Tủ sách cá nhân',
        'Quản lý đơn hàng':'Quản lý đơn hàng',
        'Thành tích':'Thành tích',
        'Lịch sử giao dịch':'Lịch sử giao dịch',
        'Hỗ trợ khách hàng':'Hỗ trợ khách hàng',
        'Trợ lý AI & Gợi ý':'Trợ lý AI & Gợi ý',
    }
    icons={
        'Trang chủ':':material/home:',
        'Tổng quan & Thống kê':':material/pie_chart:',
        'Tra cứu & Quản lý Sách':':material/menu_book:',
        'Quản lý Độc giả':':material/id_card:',
        'Quản lý Mượn / Trả / Phạt':':material/handshake:',
        'Đặt trước Sách':':material/bookmark:',
        'Tài khoản & Phân quyền':':material/groups:',
        'Trợ lý AI & Gợi ý Sách':':material/smart_toy:',
        'Báo cáo & Xuất dữ liệu':':material/file_export:',
        'Trang chủ Hội viên':':material/home:',
        'Quản lý tài khoản':':material/person:',
        'Tủ sách cá nhân':':material/library_books:',
        'Quản lý đơn hàng':':material/receipt_long:',
        'Thành tích':':material/emoji_events:',
        'Lịch sử giao dịch':':material/history:',
        'Hỗ trợ khách hàng':':material/support_agent:',
        'Trợ lý AI & Gợi ý':':material/smart_toy:',
    }

    def nav_button(item):
        selected=st.session_state.nav_page==item
        if st.button(
            labels.get(item,item),
            key='nav_'+item,
            type='primary' if selected else 'secondary',
            use_container_width=True,
            icon=icons.get(item),
        ):
            st.session_state.nav_page=item
            st.rerun()

    with st.sidebar:
        with st.container(key='sidebar_top_fixed'):
            st.markdown(
                '''<div class="side-brand">
                    <span class="brand-icon" aria-hidden="true">
                      <svg viewBox="0 0 24 24" width="28" height="28" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M6.6 4.7h4.2c1.2 0 2.2.4 3.2 1.2v12.7c-.9-.7-1.9-1.1-3.2-1.1H6.6V4.7Z" fill="white"/>
                        <path d="M17.4 4.7h-2.1v12.8c.7-.1 1.4 0 2.1.2V4.7Z" fill="white" opacity=".88"/>
                        <rect x="5" y="19" width="14" height="1.5" rx=".75" fill="white"/>
                      </svg>
                    </span>
                    <div><div class="side-title">SmartLibrary <span class="ai-badge">AI</span></div>
                    <div class="side-sub">Quản lý Thư viện 4.0</div></div>
                </div>''',
                unsafe_allow_html=True,
            )
            st.markdown(
                f'''<div class="profile-card"><div class="profile-row">
                    <span class="profile-avatar" aria-hidden="true">
                      <svg viewBox="0 0 24 24" width="25" height="25" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="9" cy="8" r="3.2" fill="#6B63F3"/>
                        <path d="M3.8 18.4c.4-3.4 2.4-5.3 5.2-5.3s4.8 1.9 5.2 5.3" fill="#6B63F3"/>
                        <circle cx="17.2" cy="11.2" r="2.3" fill="#6B63F3" opacity=".75"/>
                        <path d="M14.9 18.4c.2-2.3 1.6-3.8 3.7-3.8 1 0 1.8.3 2.5.9" fill="none" stroke="#6B63F3" stroke-width="1.8" stroke-linecap="round"/>
                      </svg>
                    </span>
                    <div><span class="role-chip">{role_name(user["role"]).upper()}</span>
                    <div class="profile-name">{html.escape(user["full_name"])}</div></div>
                </div></div>''',
                unsafe_allow_html=True,
            )

        with st.container(key='sidebar_menu_scroll'):
            if user['role'] in ('admin','librarian'):
                # Trang chủ luôn hiện ngay dưới thẻ quản trị viên.
                with st.container(key='sidebar_home_group'):
                    nav_button('Trang chủ')
                st.markdown('<div class="side-group">QUẢN LÝ THƯ VIỆN</div>',unsafe_allow_html=True)
                menu_items=core[1:]
            else:
                st.markdown('<div class="side-group">TÀI KHOẢN HỘI VIÊN</div>',unsafe_allow_html=True)
                menu_items=core

            with st.container(key='sidebar_core_group'):
                for item in menu_items:
                    nav_button(item)

            if ai_items:
                st.markdown('<div class="side-group">TÍNH NĂNG AI</div>',unsafe_allow_html=True)
                with st.container(key='sidebar_ai_group'):
                    for item in ai_items:
                        nav_button(item)

            if report_items:
                st.markdown('<div class="side-group">BÁO CÁO & XUẤT FILE</div>',unsafe_allow_html=True)
                with st.container(key='sidebar_report_group'):
                    for item in report_items:
                        nav_button(item)

        with st.container(key='sidebar_bottom_fixed'):
            theme_label='Giao diện Tối' if st.session_state.ui_theme=='light' else 'Giao diện Sáng'
            theme_icon=':material/dark_mode:' if st.session_state.ui_theme=='light' else ':material/light_mode:'
            if st.button(theme_label,use_container_width=True,key='theme_toggle_btn',icon=theme_icon):
                st.session_state.ui_theme='dark' if st.session_state.ui_theme=='light' else 'light'
                st.rerun()

            if st.button('Đăng xuất',use_container_width=True,key='logout_btn',icon=':material/logout:'):
                db.log_activity(user['id'],'Đăng xuất','Đăng xuất hệ thống')
                st.session_state.user=None
                st.session_state.public_page='home'
                st.rerun()

def app_header(user):
    ai_target = 'Trợ lý AI & Gợi ý Sách' if user['role'] in ('admin', 'librarian') else 'Trợ lý AI & Gợi ý'
    is_ai_active = st.session_state.nav_page == ai_target
    is_report_active = st.session_state.nav_page == 'Báo cáo & Xuất dữ liệu'

    c1, c2, c3, c4, c5 = st.columns([1.8, 2.3, 1.35, 1.45, 1.1], gap='small')
    with c1:
        st.markdown(
            f'<div style="font-size:.82rem;color:#8d96a8;font-weight:600">SmartLibrary / {role_name(user["role"])}</div>'
            f'<div style="font-size:1.05rem;font-weight:800;color:var(--text-main,#1e293b)">{html.escape(st.session_state.nav_page)}</div>',
            unsafe_allow_html=True
        )
    with c2:
        q = st.text_input('Tìm nhanh', placeholder='🔍 Tìm nhanh sách, độc giả...', label_visibility='collapsed', key='top_tb_search')
        if q:
            st.session_state.quick_search = q
            if user['role'] in ('admin', 'librarian'):
                st.session_state.nav_page = 'Tra cứu & Quản lý Sách'
            st.rerun()
    with c3:
        if st.button('🤖 Trợ lý AI', key='hdr_tb_ai', type='primary' if is_ai_active else 'secondary', use_container_width=True):
            st.session_state.nav_page = ai_target
            st.rerun()
    with c4:
        if user['role'] in ('admin', 'librarian'):
            if st.button('📄 Báo cáo & Xuất file', key='hdr_tb_report', type='primary' if is_report_active else 'secondary', use_container_width=True):
                st.session_state.nav_page = 'Báo cáo & Xuất dữ liệu'
                st.rerun()
        else:
            if st.button('📚 Tủ sách cá nhân', key='hdr_tb_shelf', use_container_width=True):
                st.session_state.nav_page = 'Tủ sách cá nhân'
                st.rerun()
    with c5:
        st.markdown(f'<div style="text-align:right;font-weight:800;color:var(--text-main,#3d465a);font-size:.9rem;padding-top:4px">👤 {html.escape(user["full_name"].split()[-1])}</div>', unsafe_allow_html=True)
    st.divider()

# ------------------------------------------------------------------
# STAFF PAGES
# ------------------------------------------------------------------
def staff_home(user):
    stats,categories,months=db.admin_stats()
    st.markdown(
        f'<div class="staff-home-hero"><div class="staff-home-kicker">TRANG CHỦ QUẢN TRỊ</div>'
        f'<div class="staff-home-title">Chào mừng trở lại, {html.escape(user["full_name"])}! 👋</div>'
        f'<div class="staff-home-sub">Từ đây bạn có thể mở nhanh các khu vực quản lý hoặc xem tình trạng thư viện hôm nay.</div></div>',
        unsafe_allow_html=True
    )

    st.markdown('<div class="mini-title">⚡ Truy cập nhanh hệ thống</div>',unsafe_allow_html=True)
    qcols=st.columns(3,gap='medium')
    quick_top=[
        ('q1','📚','Quản lý Sách','Tra cứu, thêm, sửa và kiểm tra kho sách','Tra cứu & Quản lý Sách'),
        ('q2','👥','Quản lý Độc giả','Hồ sơ, trạng thái thẻ và thông tin độc giả','Quản lý Độc giả'),
        ('q4','⇄','Mượn / Trả / Phạt','Duyệt mượn, xác nhận trả và xử lý tiền phạt','Quản lý Mượn / Trả / Phạt'),
    ]
    for i,(clazz,ico,name,desc,target) in enumerate(quick_top):
        with qcols[i]:
            st.markdown(f'<div class="quick-card {clazz}"><div class="quick-icon">{ico}</div><div class="quick-name">{name}</div><div class="quick-desc">{desc}</div></div>',unsafe_allow_html=True)
            if st.button('Mở →',key=f'home_open_top_{i}',use_container_width=True):
                st.session_state.nav_page=target
                st.rerun()

    st.write('')
    qcols2=st.columns(3,gap='medium')
    quick_bot=[
        ('q5','🔖','Đặt trước Sách','Quản lý phiếu hẹn và giữ sách cho độc giả','Đặt trước Sách'),
        ('q3','🤖','Trợ lý AI & Gợi ý','Hỏi đáp thông minh RAG, tóm tắt & gợi ý sách','Trợ lý AI & Gợi ý Sách'),
        ('q6','📄','Báo cáo & Xuất file','Xem báo cáo vận hành & tải xuống file CSV','Báo cáo & Xuất dữ liệu'),
    ]
    for i,(clazz,ico,name,desc,target) in enumerate(quick_bot):
        with qcols2[i]:
            st.markdown(f'<div class="quick-card {clazz}"><div class="quick-icon">{ico}</div><div class="quick-name">{name}</div><div class="quick-desc">{desc}</div></div>',unsafe_allow_html=True)
            if st.button('Mở →',key=f'home_open_bot_{i}',use_container_width=True):
                st.session_state.nav_page=target
                st.rerun()

    st.write('')
    mcols=st.columns(4)
    metric_data=[
        ('📚 Tổng đầu sách',stats['titles'],'Toàn bộ danh mục'),
        ('👥 Độc giả hoạt động',stats['readers'],'Tài khoản đang hoạt động'),
        ('📖 Đang mượn',stats['borrowed'],'Bao gồm phiếu chưa hoàn tất'),
        ('⚠️ Quá hạn',stats['overdue'],'Cần xử lý sớm'),
    ]
    for c,(label,val,note) in zip(mcols,metric_data):
        with c:
            st.markdown(f'<div class="home-metric"><div class="home-metric-label">{label}</div><div class="home-metric-value">{val}</div><div class="home-metric-note">{note}</div></div>',unsafe_allow_html=True)

    st.write('')
    left,right=st.columns([1.6,1],gap='large')
    with left:
        st.markdown('<div class="home-panel"><div class="home-panel-title">📈 Hoạt động mượn sách gần đây</div>',unsafe_allow_html=True)
        if months:
            st.bar_chart(pd.DataFrame(months).set_index('month')['total'],height=260)
        else:
            st.info('Chưa có dữ liệu mượn sách.')
        st.markdown('</div>',unsafe_allow_html=True)
    with right:
        st.markdown('<div class="home-panel"><div class="home-panel-title">📌 Việc cần chú ý</div>',unsafe_allow_html=True)
        st.write(f"**{stats['pending']}** yêu cầu mượn đang chờ duyệt")
        st.write(f"**{stats['reservations']}** lượt đặt trước đang chờ")
        st.write(f"**{stats['overdue']}** phiếu đang quá hạn")
        st.write(f"**{money(stats['unpaid_fines'])}** tiền phạt chưa thu")
        if st.button('Xem Tổng quan & Thống kê',key='home_to_dashboard',type='primary',use_container_width=True):
            st.session_state.nav_page='Tổng quan & Thống kê'; st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)

    st.write('')
    a,b=st.columns([1.2,1],gap='large')
    with a:
        st.markdown('<div class="home-panel"><div class="home-panel-title">🕘 Hoạt động gần đây</div>',unsafe_allow_html=True)
        acts=db.list_activity(6)
        if acts:
            for x in acts:
                who=x.get('full_name') or 'Hệ thống'
                st.markdown(f'<div class="activity-row"><div class="activity-title">{html.escape(who)} · {html.escape(x["action"])}</div><div class="activity-detail">{html.escape(x.get("detail") or "")} · {html.escape(x.get("created_at") or "")}</div></div>',unsafe_allow_html=True)
        else:
            st.caption('Chưa có nhật ký hoạt động.')
        st.markdown('</div>',unsafe_allow_html=True)
    with b:
        st.markdown('<div class="home-panel"><div class="home-panel-title">🔥 Sách nổi bật</div>',unsafe_allow_html=True)
        top=db.top_borrowed_books(5)
        if top:
            for idx,bk in enumerate(top[:5],1):
                st.write(f"**{idx}. {bk['title']}**")
                st.caption(f"{bk['author']} · {bk.get('borrow_count',0)} lượt mượn")
        else:
            st.caption('Chưa có dữ liệu.')
        st.markdown('</div>',unsafe_allow_html=True)


def dashboard_page(user):
    stats,categories,months=db.admin_stats()
    page_head('Tổng quan & Thống kê','Theo dõi tình hình vận hành thư viện theo thời gian thực')
    cols=st.columns(5)
    cards=[('📚','Đầu sách',stats['titles']),('👥','Độc giả',stats['readers']),('📖','Đang mượn',stats['borrowed']),('⚠️','Quá hạn',stats['overdue']),('🔖','Đặt trước',stats['reservations'])]
    for col,(ico,label,val) in zip(cols,cards):
        with col: st.markdown(f'<div class="metric-card"><div class="metric-label">{ico} {label}</div><div class="metric-value">{val}</div></div>',unsafe_allow_html=True)
    st.write('')
    a,b=st.columns([1.3,1],gap='large')
    with a:
        st.markdown('<div class="panel"><div class="mini-title">📈 Lượt mượn theo tháng</div>',unsafe_allow_html=True)
        if months: st.line_chart(pd.DataFrame(months).set_index('month')['total'],height=270)
        else: st.info('Chưa có dữ liệu mượn.')
        st.markdown('</div>',unsafe_allow_html=True)
    with b:
        st.markdown('<div class="panel"><div class="mini-title">📊 Phân bố thể loại</div>',unsafe_allow_html=True)
        if categories: st.bar_chart(pd.DataFrame(categories[:8]).set_index('category')['titles'],height=270)
        st.markdown('</div>',unsafe_allow_html=True)
    c,d=st.columns([1.2,1],gap='large')
    with c:
        st.subheader('⏳ Yêu cầu mượn chờ duyệt')
        pending=db.list_loans('pending')[:6]
        if pending: st.dataframe(pd.DataFrame(pending)[['id','member_code','full_name','book_id','title','request_date']],use_container_width=True,hide_index=True)
        else: st.success('Không có yêu cầu đang chờ.')
    with d:
        st.subheader('🕘 Hoạt động gần đây')
        acts=db.list_activity(7)
        if acts:
            for x in acts: st.write(f"**{x.get('full_name') or 'Hệ thống'}** · {x['action']}"); st.caption(x.get('detail') or '')
        else: st.caption('Chưa có nhật ký hoạt động.')
    st.subheader('🔥 Sách được mượn nhiều')
    top=db.top_borrowed_books(5)
    if top: st.dataframe(pd.DataFrame(top)[['id','title','author','category','borrow_count','available']],use_container_width=True,hide_index=True)


def books_page(user):
    st.markdown('<div class="books-page-marker"></div>',unsafe_allow_html=True)

    # Header similar to the reference management UI.
    h1,h2,h3,h4=st.columns([4.8,2.25,1.45,1.05],gap='small')
    with h1:
        st.markdown('<div class="book-page-heading">Tra cứu & Quản lý Sách</div><div class="book-page-sub">Danh mục đầu sách, tìm kiếm và quản lý kho sách</div>',unsafe_allow_html=True)
    with h2:
        top_q=st.text_input('Tìm nhanh',placeholder='🔍  Tìm nhanh sách, độc giả...',label_visibility='collapsed',key='book_top_quick_search')
    with h3:
        if st.button('＋ Tạo Phiếu mượn',type='primary',use_container_width=True,key='book_go_create_loan'):
            st.session_state.nav_page='Quản lý Mượn / Trả / Phạt'
            st.rerun()
    with h4:
        if st.button('↪ Đăng xuất',use_container_width=True,key='book_top_logout'):
            db.log_activity(user['id'],'Đăng xuất','Đăng xuất hệ thống')
            st.session_state.user=None
            st.rerun()

    all_books=db.list_books()
    total_copies=sum(int(x.get('quantity') or 0) for x in all_books)
    available_copies=sum(int(x.get('available') or 0) for x in all_books)
    out_titles=sum(1 for x in all_books if int(x.get('available') or 0)<=0)
    cats=len({x.get('category') for x in all_books if x.get('category')})
    kcols=st.columns(4,gap='small')
    for col,(label,val,note) in zip(kcols,[
        ('📚 Đầu sách',len(all_books),f'{total_copies} bản trong kho'),
        ('✅ Sẵn sàng',available_copies,'Bản có thể cho mượn'),
        ('⚠️ Hết sách',out_titles,'Đầu sách cần bổ sung'),
        ('🏷️ Thể loại',cats,'Danh mục đang quản lý'),
    ]):
        with col:
            st.markdown(f'<div class="book-kpi"><div class="book-kpi-label">{label}</div><div class="book-kpi-value">{val}</div><div class="book-kpi-note">{note}</div></div>',unsafe_allow_html=True)

    # Dialogs keep the page compact instead of pushing forms under the catalog.
    @st.dialog('Thêm Sách Mới', width='medium')
    def add_book_dialog():
        st.markdown('<div class="book-dialog-marker"></div>', unsafe_allow_html=True)
        with st.form('v17_add_book_form'):
            a,b=st.columns(2)
            with a:
                bid=st.text_input('Mã sách',placeholder='MS005')
                title=st.text_input('Tên sách')
                author=st.text_input('Tác giả')
                isbn=st.text_input('ISBN')
            with b:
                typ=st.text_input('Loại',value='Sách')
                category=st.text_input('Thể loại')
                publisher=st.text_input('Nhà xuất bản')
                year=st.number_input('Năm xuất bản',1900,2100,2026)
            c,d=st.columns(2)
            with c: qty=st.number_input('Số lượng',1,10000,1)
            with d: location=st.text_input('Vị trí kệ',placeholder='A1-01')
            desc=st.text_area('Mô tả')
            submit=st.form_submit_button('＋ Thêm Sách Mới',type='primary',use_container_width=True)
        if submit:
            ok,msg=db.add_book({'id':bid.strip().upper(),'title':title,'author':author,'type':typ,'category':category,'year':year,'quantity':qty,'location':location,'description':desc,'cover_image':'','isbn':isbn,'publisher':publisher})
            if ok: db.log_activity(user['id'],'Thêm sách',f'{bid} - {title}')
            (st.success if ok else st.error)(msg)
            if ok: st.rerun()

    @st.dialog('Sửa thông tin sách', width='medium')
    def edit_book_dialog(book_id):
        st.markdown('<div class="book-dialog-marker"></div>', unsafe_allow_html=True)
        bk=db.get_book(book_id)
        if not bk:
            st.error('Không tìm thấy đầu sách.')
            return
        with st.form('v17_edit_book_form'):
            a,b=st.columns(2)
            with a:
                title=st.text_input('Tên sách',bk['title'])
                author=st.text_input('Tác giả',bk['author'])
                isbn=st.text_input('ISBN',bk.get('isbn') or '')
                publisher=st.text_input('Nhà xuất bản',bk.get('publisher') or '')
            with b:
                typ=st.text_input('Loại',bk['type'])
                category=st.text_input('Thể loại',bk['category'])
                year=st.number_input('Năm',1900,2100,int(bk.get('year') or 2026))
                qty=st.number_input('Số lượng',0,10000,int(bk['quantity']))
            location=st.text_input('Vị trí kệ',bk.get('location') or '')
            desc=st.text_area('Mô tả',bk.get('description') or '')
            save=st.form_submit_button('💾 Lưu thay đổi',type='primary',use_container_width=True)
        if save:
            ok,msg=db.update_book(book_id,{'title':title,'author':author,'type':typ,'category':category,'year':year,'quantity':qty,'location':location,'description':desc,'cover_image':bk.get('cover_image') or '','isbn':isbn,'publisher':publisher})
            if ok: db.log_activity(user['id'],'Cập nhật sách',f'{book_id} - {title}')
            (st.success if ok else st.error)(msg)
            if ok: st.rerun()

    @st.dialog('Xóa đầu sách', width='small')
    def delete_book_dialog(book_id):
        bk=db.get_book(book_id)
        if not bk:
            st.error('Không tìm thấy đầu sách.')
            return
        st.warning(f'Bạn có chắc muốn xóa **{bk["title"]}** (`{book_id}`)?')
        c1,c2=st.columns(2)
        with c1:
            if st.button('Hủy',use_container_width=True,key='v17_del_cancel'): st.rerun()
        with c2:
            if st.button('🗑️ Xóa',type='primary',use_container_width=True,key='v17_del_confirm'):
                ok,msg=db.delete_book(book_id)
                if ok: db.log_activity(user['id'],'Xóa sách',book_id)
                (st.success if ok else st.error)(msg)
                if ok: st.rerun()

    @st.dialog('AI Tóm tắt sách', width='medium')
    def ai_summary_dialog(book_id):
        bk=db.get_book(book_id)
        if not bk:
            st.error('Không tìm thấy sách.')
            return
        cache=st.session_state.setdefault('book_ai_summary_cache',{})
        if book_id not in cache:
            ai=get_ai_service()
            prompt=(f'Tóm tắt ngắn gọn cuốn sách "{bk["title"]}" của {bk["author"]}. '
                    f'Dữ liệu thư viện: thể loại {bk.get("category")}; mô tả: {bk.get("description") or "chưa có"}. '
                    'Trả lời 4-6 câu bằng tiếng Việt, không bịa thông tin ngoài dữ liệu nếu không chắc.')
            with st.spinner('AI đang tóm tắt...'):
                cache[book_id]=ai.answer(prompt,[])
        st.markdown(f'### {bk["title"]}')
        st.markdown(f'<div class="book-ai-result">{cache[book_id]}</div>',unsafe_allow_html=True)

    @st.dialog('Tạo yêu cầu mượn', width='medium')
    def borrow_book_dialog(book_id):
        bk=db.get_book(book_id)
        readers=db.list_users('reader','active')
        st.markdown(f'**Sách:** {bk["title"] if bk else book_id}')
        if not readers:
            st.info('Chưa có độc giả hoạt động để tạo phiếu mượn.')
            return
        options=[r['id'] for r in readers]
        uid=st.selectbox('Chọn độc giả',options,format_func=lambda x: next(f"{r.get('member_code') or ''} — {r['full_name']}" for r in readers if r['id']==x))
        if st.button('🤝 Tạo yêu cầu mượn',type='primary',use_container_width=True,key='v17_borrow_submit'):
            ok,msg=db.request_borrow(uid,book_id)
            if ok: db.log_activity(user['id'],'Tạo yêu cầu mượn',f'{book_id} cho user {uid}')
            (st.success if ok else st.error)(msg)

    # Filters / view switch matching the reference.
    st.markdown('<div class="book-filter-shell">',unsafe_allow_html=True)
    f1,f2,f3,f4,f5,f6=st.columns([3.0,1.35,1.15,.28,.28,1.15],gap='small')
    with f1:
        q=st.text_input('Tìm sách',placeholder='🔍  Tìm theo tên sách, tác giả, mã sách...',label_visibility='collapsed',key='v17_book_search')
    with f2:
        cat=st.selectbox('Thể loại',['Tất cả thể loại']+db.list_categories(),label_visibility='collapsed',key='v17_book_cat')
    with f3:
        status=st.selectbox('Trạng thái',['Tất cả trạng thái','Còn sách','Sắp hết','Hết sách'],label_visibility='collapsed',key='v17_book_status')
    with f4:
        if st.button('▦',use_container_width=True,key='book_view_grid',type='primary' if st.session_state.get('book_view_mode','grid')=='grid' else 'secondary'):
            st.session_state.book_view_mode='grid';st.rerun()
    with f5:
        if st.button('☷',use_container_width=True,key='book_view_list',type='primary' if st.session_state.get('book_view_mode','grid')=='list' else 'secondary'):
            st.session_state.book_view_mode='list';st.rerun()
    with f6:
        if st.button('＋ Thêm Sách Mới',type='primary',use_container_width=True,key='v17_add_book_btn'): add_book_dialog()
    st.markdown('</div>',unsafe_allow_html=True)

    query=(top_q or q or '').strip()
    db_cat='Tất cả' if cat=='Tất cả thể loại' else cat
    books=db.list_books(query,db_cat,False,'Tất cả')
    if status=='Còn sách': books=[b for b in books if int(b.get('available') or 0)>1]
    elif status=='Sắp hết': books=[b for b in books if int(b.get('available') or 0)==1]
    elif status=='Hết sách': books=[b for b in books if int(b.get('available') or 0)<=0]

    if query:
        st.caption(f'🎯 Tìm thấy {len(books)} kết quả cho “{query}”. Kết quả BM25 được giữ theo độ liên quan.')

    view=st.session_state.get('book_view_mode','grid')
    if not books:
        st.markdown('<div class="book-empty-msg">📚 Không có đầu sách phù hợp với bộ lọc hiện tại.</div>',unsafe_allow_html=True)
        return

    if view=='list':
        data=[]
        for bk in books:
            data.append({'Mã':bk['id'],'Tên sách':bk['title'],'Tác giả':bk['author'],'Thể loại':bk['category'],'Tồn kho':f"{bk['available']}/{bk['quantity']}",'Vị trí':bk.get('location') or '—','Lượt xem':bk.get('view_count',0)})
        st.dataframe(pd.DataFrame(data),use_container_width=True,hide_index=True,height=560)
        sid=st.selectbox('Chọn sách để thao tác',[b['id'] for b in books],format_func=lambda x:f"{x} — {next(z['title'] for z in books if z['id']==x)}",key='v17_list_selected')
        x1,x2,x3,x4=st.columns(4)
        with x1:
            if st.button('✨ AI Tóm tắt',use_container_width=True,key='v17_list_ai'): ai_summary_dialog(sid)
        with x2:
            if st.button('🤝 Mượn sách',use_container_width=True,key='v17_list_borrow'): borrow_book_dialog(sid)
        with x3:
            if st.button('✎ Sửa',use_container_width=True,key='v17_list_edit'): edit_book_dialog(sid)
        with x4:
            if st.button('🗑 Xóa',use_container_width=True,key='v17_list_delete'): delete_book_dialog(sid)
        return

    # Grid view: 4 cards/row like the reference screenshot.
    max_show=12
    shown=books[:max_show]
    for start_i in range(0,len(shown),4):
        cols=st.columns(4,gap='medium')
        for col,bk in zip(cols,shown[start_i:start_i+4]):
            with col:
                with st.container(key=f'book_card_{bk["id"]}'):
                    cp=cover(bk)
                    if cp: st.image(str(cp),use_container_width=True)
                    else: st.markdown('<div class="book-card-cover-empty">📖</div>',unsafe_allow_html=True)
                    st.markdown(
                        f'<div class="book-card-body"><div class="book-card-category">{html.escape(bk.get("category") or "Khác")} • {html.escape(bk["id"])}</div>'
                        f'<div class="book-card-title">{html.escape(bk["title"])}</div>'
                        f'<div class="book-card-author">✒ {html.escape(bk.get("author") or "—")}</div>'
                        f'<div class="book-card-divider"></div>'
                        f'<div class="book-card-stock"><span>▤ Tồn: {bk.get("available",0)}/{bk.get("quantity",0)}</span><span>⌖ Kệ {html.escape(bk.get("location") or "—")}</span></div></div>',
                        unsafe_allow_html=True,
                    )
                    a1,a2=st.columns(2,gap='small')
                    with a1:
                        if st.button('AI Tóm tắt',use_container_width=True,key=f'ai_sum_{bk["id"]}'): ai_summary_dialog(bk['id'])
                    with a2:
                        if st.button('🤝 Mượn sách',type='primary',use_container_width=True,key=f'borrow_{bk["id"]}'): borrow_book_dialog(bk['id'])
                    e1,e2=st.columns([1,1],gap='small')
                    with e1:
                        if st.button('✎ Sửa',use_container_width=True,key=f'edit_{bk["id"]}'): edit_book_dialog(bk['id'])
                    with e2:
                        if st.button('🗑 Xóa',use_container_width=True,key=f'del_{bk["id"]}'): delete_book_dialog(bk['id'])

    if len(books)>max_show:
        st.caption(f'Đang hiển thị {max_show}/{len(books)} đầu sách. Dùng ô tìm kiếm hoặc bộ lọc để thu hẹp kết quả.')

def readers_page(user):
    st.markdown('<div class="reader-mgmt-marker"></div>',unsafe_allow_html=True)

    @st.dialog('Cấp Thẻ Độc Giả Mới', width='medium')
    def add_reader_dialog():
        st.caption('Tạo tài khoản độc giả mới và cấp thẻ thư viện ngay trên hệ thống.')
        with st.form('v18_add_reader_form'):
            a,b=st.columns(2)
            with a:
                username=st.text_input('Tên đăng nhập',placeholder='dg004')
                full_name=st.text_input('Họ và tên',placeholder='Nguyễn Văn A')
                email=st.text_input('Email',placeholder='reader@email.com')
            with b:
                phone=st.text_input('Số điện thoại',placeholder='09xxxxxxxx')
                password=st.text_input('Mật khẩu ban đầu',value='reader123',type='password')
                card_type=st.selectbox('Loại độc giả',['Sinh viên','Giảng viên','Khác'])
            submitted=st.form_submit_button('🪪 Cấp Thẻ Độc Giả Mới',type='primary',use_container_width=True)
        if submitted:
            ok,msg=auth.register_reader(username,password,full_name,email,phone)
            if ok:
                created=db.get_user_by_username(username)
                if created:
                    db.update_reader_admin(created['id'],full_name,email,phone,card_type,created.get('card_expiry') or '',created.get('address') or '',created.get('max_books') or int(db.get_setting('max_books_per_reader',5)),'active')
                    db.log_activity(user['id'],'Cấp thẻ độc giả',f'{created.get("member_code") or username} - {full_name}')
                st.success('Đã tạo độc giả và cấp thẻ thành công.')
                st.rerun()
            else:
                st.error(msg)

    @st.dialog('Sửa thông tin độc giả', width='medium')
    def edit_reader_dialog(uid):
        rd=db.get_user(uid)
        if not rd:
            st.error('Không tìm thấy độc giả.'); return
        with st.form(f'v18_edit_reader_{uid}'):
            a,b=st.columns(2)
            with a:
                name=st.text_input('Họ và tên',rd.get('full_name') or '')
                email=st.text_input('Email',rd.get('email') or '')
                phone=st.text_input('Số điện thoại',rd.get('phone') or '')
                address=st.text_input('Địa chỉ',rd.get('address') or '')
            with b:
                types=['Sinh viên','Giảng viên','Khác']
                current=rd.get('card_type') or 'Sinh viên'
                card=st.selectbox('Loại độc giả',types,index=types.index(current) if current in types else 0)
                expiry=st.text_input('Ngày hết hạn',rd.get('card_expiry') or '')
                maxb=st.number_input('Giới hạn mượn',1,50,int(rd.get('max_books') or db.get_setting('max_books_per_reader',5)))
                stat=st.selectbox('Trạng thái',['active','locked'],index=0 if rd.get('status')=='active' else 1,format_func=status_vi)
            save=st.form_submit_button('💾 Lưu thay đổi',type='primary',use_container_width=True)
        if save:
            db.update_reader_admin(uid,name,email,phone,card,expiry,address,maxb,stat)
            db.log_activity(user['id'],'Cập nhật độc giả',rd.get('member_code') or str(uid))
            st.success('Đã cập nhật thông tin độc giả.')
            st.rerun()

    @st.dialog('Chi tiết độc giả', width='large')
    def reader_detail_dialog(uid):
        rd=db.get_user(uid)
        if not rd:
            st.error('Không tìm thấy độc giả.'); return
        loans=db.reader_loans(uid)
        reservations=db.reader_reservations(uid)
        fines=[x for x in db.list_fines('Tất cả') if x['user_id']==uid]
        st.markdown(f'### {rd.get("full_name") or "Độc giả"}')
        st.caption(f'{rd.get("member_code") or "—"} · @{rd.get("username") or "—"} · {status_vi(rd.get("status") or "active")}')
        c1,c2,c3=st.columns(3)
        c1.metric('Đang mượn',sum(1 for x in loans if x.get('status') in ('borrowed','overdue','return_requested')))
        c2.metric('Đặt trước',sum(1 for x in reservations if x.get('status')=='pending'))
        c3.metric('Phạt chưa thu',money(sum(int(x.get('amount') or 0) for x in fines if x.get('status')=='unpaid')))
        t1,t2,t3=st.tabs(['📚 Lịch sử mượn','🔖 Đặt trước','💳 Tiền phạt'])
        with t1:
            if loans: st.dataframe(pd.DataFrame(loans)[['id','book_id','title','request_date','due_date','returned_date','status','fine_amount']],use_container_width=True,hide_index=True)
            else: st.info('Độc giả chưa có lịch sử mượn.')
        with t2:
            if reservations: st.dataframe(pd.DataFrame(reservations)[['id','book_id','title','created_at','status','handled_at']],use_container_width=True,hide_index=True)
            else: st.info('Chưa có yêu cầu đặt trước.')
        with t3:
            if fines: st.dataframe(pd.DataFrame(fines)[['id','title','amount','reason','status','created_at','paid_at']],use_container_width=True,hide_index=True)
            else: st.success('Không có khoản phạt chưa xử lý.')

    # Header like the reference screenshot.
    h1,h2,h3,h4=st.columns([4.7,2.15,1.45,1.05],gap='small')
    with h1:
        st.markdown('<div class="reader-page-heading">Quản lý Độc giả</div><div class="reader-page-sub">Danh sách thẻ thư viện, gia hạn và theo dõi trạng thái độc giả</div>',unsafe_allow_html=True)
    with h2:
        top_q=st.text_input('Tìm nhanh độc giả',placeholder='🔍  Tìm nhanh sách, độc giả...',label_visibility='collapsed',key='reader_top_quick_search')
    with h3:
        if st.button('＋ Tạo Phiếu mượn',type='primary',use_container_width=True,key='reader_go_loan'):
            st.session_state.nav_page='Quản lý Mượn / Trả / Phạt'; st.rerun()
    with h4:
        if st.button('↪ Đăng xuất',use_container_width=True,key='reader_logout_top'):
            db.log_activity(user['id'],'Đăng xuất','Đăng xuất hệ thống')
            st.session_state.user=None; st.session_state.public_page='home'; st.rerun()

    st.markdown('<div class="reader-filter-shell"></div>',unsafe_allow_html=True)
    f1,f2,f3=st.columns([4.1,1.25,1.55],gap='small')
    with f1:
        q=st.text_input('Tìm độc giả',placeholder='🔍  Tìm theo tên độc giả, mã thẻ, email, SĐT...',label_visibility='collapsed',key='v18_reader_search')
    with f2:
        status=st.selectbox('Trạng thái',['Tất cả','active','locked'],label_visibility='collapsed',format_func=lambda x:'Tất cả trạng thái' if x=='Tất cả' else status_vi(x),key='v18_reader_status')
    with f3:
        if st.button('🪪  Cấp Thẻ Độc Giả Mới',type='primary',use_container_width=True,key='v18_reader_add'): add_reader_dialog()

    query=(top_q or q or '').strip()
    readers=db.list_users('reader',status,query)

    if not readers:
        st.markdown('<div class="reader-empty">👥 Không tìm thấy độc giả phù hợp với bộ lọc hiện tại.</div>',unsafe_allow_html=True)
        return

    # Table header
    st.markdown('<div class="reader-table-card">',unsafe_allow_html=True)
    heads=st.columns([.72,1.5,2.0,1.05,1.05,1.05,1.05,1.05],gap='small')
    labels=['Mã thẻ','Họ và Tên','Liên hệ (Email / SĐT)','Loại độc giả','Trạng thái','Ngày cấp','Ngày hết hạn','Hành động']
    for col,label in zip(heads,labels):
        with col: st.markdown(f'<div class="reader-table-head">{label}</div>',unsafe_allow_html=True)

    # Table body. Keep rows compact and functional.
    for rd in readers[:30]:
        cols=st.columns([.72,1.5,2.0,1.05,1.05,1.05,1.05,1.05],gap='small')
        created=(rd.get('created_at') or '—')[:10]
        expiry=rd.get('card_expiry') or '—'
        with cols[0]: st.markdown(f'<div class="reader-row reader-code">{html.escape(rd.get("member_code") or "—")}</div>',unsafe_allow_html=True)
        with cols[1]: st.markdown(f'<div class="reader-row"><div class="reader-name">{html.escape(rd.get("full_name") or "—")}</div><div class="reader-user">Tài khoản: {html.escape(rd.get("username") or "—")}</div></div>',unsafe_allow_html=True)
        with cols[2]: st.markdown(f'<div class="reader-row reader-contact">✉ {html.escape(rd.get("email") or "—")}<br>☎ {html.escape(rd.get("phone") or "—")}</div>',unsafe_allow_html=True)
        with cols[3]: st.markdown(f'<div class="reader-row"><span class="reader-pill type">{html.escape(rd.get("card_type") or "Độc giả")}</span></div>',unsafe_allow_html=True)
        status_cls='active' if rd.get('status')=='active' else 'locked'
        with cols[4]: st.markdown(f'<div class="reader-row"><span class="reader-pill {status_cls}">{status_vi(rd.get("status") or "active")}</span></div>',unsafe_allow_html=True)
        with cols[5]: st.markdown(f'<div class="reader-row reader-date">{html.escape(created)}</div>',unsafe_allow_html=True)
        with cols[6]: st.markdown(f'<div class="reader-row reader-date">{html.escape(expiry)}</div>',unsafe_allow_html=True)
        with cols[7]:
            st.markdown('<div class="reader-actions">',unsafe_allow_html=True)
            a1,a2,a3=st.columns([1.2,.7,.7],gap='small')
            with a1:
                if st.button('✎ Sửa',key=f'v18_edit_reader_{rd["id"]}',use_container_width=True): edit_reader_dialog(rd['id'])
            with a2:
                lock_icon='🔓' if rd.get('status')=='locked' else '🔒'
                if st.button(lock_icon,key=f'v18_lock_reader_{rd["id"]}',use_container_width=True):
                    new_status='active' if rd.get('status')=='locked' else 'locked'
                    db.set_user_status(rd['id'],new_status)
                    db.log_activity(user['id'],'Đổi trạng thái độc giả',f'{rd.get("member_code")}: {new_status}')
                    st.rerun()
            with a3:
                if st.button('⋯',key=f'v18_detail_reader_{rd["id"]}',use_container_width=True): reader_detail_dialog(rd['id'])
            st.markdown('</div>',unsafe_allow_html=True)
    st.markdown('</div>',unsafe_allow_html=True)

    if len(readers)>30:
        st.caption(f'Đang hiển thị 30/{len(readers)} độc giả. Dùng ô tìm kiếm để thu hẹp kết quả.')

def _loan_status_badge(status):
    mapping={
        'pending':('Chờ duyệt','#fff7dd','#9a6a00'),
        'borrowed':('Đang mượn','#e8f0ff','#315fd6'),
        'overdue':('Quá hạn','#fff0e5','#d45b00'),
        'return_requested':('Chờ trả','#e9fbf4','#0a8f69'),
        'returned':('Đã trả','#edf9ef','#27834b'),
        'lost':('Không trả / Mất','#ffe9ee','#c92f55'),
        'lost_resolved':('Đã xử lý','#f0ebff','#7153cf'),
        'rejected':('Từ chối','#f3f4f6','#687083'),
    }
    label,bg,fg=mapping.get(status,(status or '—','#f3f4f6','#5c6576'))
    return f'<span style="display:inline-block;padding:5px 10px;border-radius:999px;background:{bg};color:{fg};font-weight:800;font-size:.78rem">{label}</span>'


def _loan_empty(icon,title,text):
    st.markdown(f"""<div style="background:#fff;border:1px solid #e6e9f2;border-radius:20px;padding:28px;text-align:center;color:#647086;box-shadow:0 8px 24px rgba(54,64,97,.05)">
        <div style="font-size:2rem;margin-bottom:8px">{icon}</div>
        <div style="font-weight:900;color:#26354d;font-size:1.02rem">{title}</div>
        <div style="margin-top:5px">{text}</div>
    </div>""",unsafe_allow_html=True)


def loans_fines_page(user):
    page_head('Quản lý Mượn / Trả / Phạt','Duyệt mượn, xác nhận trả, theo dõi quá hạn và nghĩa vụ tài chính')

    # Một lần đọc dữ liệu cho mỗi lượt render để trang nhẹ hơn.
    pending_rows=db.list_loans('pending')
    borrowed_rows=db.list_loans('borrowed')
    overdue_rows=db.list_loans('overdue')
    return_rows=db.list_loans('return_requested')
    lost_rows=db.list_loans('lost')
    fines_all=db.list_fines('Tất cả')

    unpaid_total=sum(int(x.get('amount') or 0) for x in fines_all if x.get('status')=='unpaid')
    cols=st.columns(5)
    cards=[
        ('⏳','Chờ duyệt',len(pending_rows),'Yêu cầu mới'),
        ('📖','Đang mượn',len(borrowed_rows),'Phiếu đang hiệu lực'),
        ('⚠️','Quá hạn',len(overdue_rows),'Cần theo dõi'),
        ('↩️','Chờ trả',len(return_rows),'Đợi xác nhận'),
        ('💳','Phạt chưa thu',money(unpaid_total),'Công nợ hiện tại'),
    ]
    for col,(ico,label,val,note) in zip(cols,cards):
        fs='1.16rem' if isinstance(val,str) else '1.68rem'
        with col:
            st.markdown(f'<div class="admin-summary-card"><div class="admin-summary-label">{ico} {label}</div><div class="admin-summary-value" style="font-size:{fs}">{val}</div><div class="admin-summary-note">{note}</div></div>',unsafe_allow_html=True)

    st.write('')
    q=st.text_input('Tìm trong phiếu mượn',placeholder='Tên độc giả, mã thẻ, mã sách hoặc tên sách...',key='loan_admin_search')
    def matched(rows):
        k=(q or '').strip().lower()
        if not k: return rows
        return [r for r in rows if k in ' '.join(str(r.get(x) or '').lower() for x in ('id','member_code','full_name','book_id','title'))]

    t1,t2,t3,t4,t5=st.tabs(['⏳ Yêu cầu mượn','📖 Đang mượn / Quá hạn','↩️ Chờ trả','💳 Tiền phạt','⚠️ Không trả / Mất'])

    with t1:
        rows=matched(pending_rows)
        if not rows:
            _loan_empty('✅','Không có yêu cầu chờ duyệt','Các yêu cầu mượn mới sẽ xuất hiện tại đây.')
        else:
            for l in rows:
                with st.container(border=True):
                    a,b,c,d=st.columns([1.1,2.2,3.1,2.1])
                    with a:
                        st.caption('MÃ PHIẾU'); st.markdown(f"**#{l['id']}**")
                    with b:
                        st.caption('ĐỘC GIẢ'); st.markdown(f"**{l.get('full_name') or '—'}**"); st.caption(l.get('member_code') or '')
                    with c:
                        st.caption('SÁCH'); st.markdown(f"**{l.get('title') or '—'}**"); st.caption(l.get('book_id') or '')
                    with d:
                        c1,c2=st.columns(2)
                        with c1:
                            if st.button('✓ Duyệt',key=f'v21_appr_{l["id"]}',type='primary',use_container_width=True):
                                ok,msg=db.approve_loan(l['id'],user['id']); (st.success if ok else st.error)(msg); st.rerun()
                        with c2:
                            if st.button('Từ chối',key=f'v21_rej_{l["id"]}',use_container_width=True):
                                ok,msg=db.reject_loan(l['id'],user['id']); (st.success if ok else st.error)(msg); st.rerun()
                    st.caption(f"Yêu cầu lúc: {l.get('request_date') or '—'}")

    with t2:
        rows=matched(borrowed_rows+overdue_rows)
        if overdue_rows:
            st.warning(f"Có {len(overdue_rows)} phiếu quá hạn. Phí được tính tự động theo cấu hình; ngưỡng tự khóa: {db.get_setting('auto_lock_overdue_days',30)} ngày.")
        if not rows:
            _loan_empty('📚','Không có sách đang mượn','Các phiếu đã duyệt hoặc quá hạn sẽ xuất hiện tại đây.')
        else:
            head=st.columns([.7,1.6,2.5,1.2,1.2,1.2])
            for col,label in zip(head,['Phiếu','Độc giả','Sách','Hạn trả','Trạng thái','Tiền phạt']):
                with col: st.markdown(f'<div style="font-size:.78rem;font-weight:900;color:#7a8497;padding-bottom:7px">{label}</div>',unsafe_allow_html=True)
            for l in rows:
                cols2=st.columns([.7,1.6,2.5,1.2,1.2,1.2])
                values=[f"#{l['id']}",f"{l.get('full_name') or '—'}\n{l.get('member_code') or ''}",f"{l.get('title') or '—'}\n{l.get('book_id') or ''}",l.get('due_date') or '—',None,money(int(l.get('fine_amount') or 0))]
                for i,(col,val) in enumerate(zip(cols2,values)):
                    with col:
                        if i==4: st.markdown(_loan_status_badge(l.get('status')),unsafe_allow_html=True)
                        elif i in (1,2):
                            aa,bb=(val.split('\n',1)+[''])[:2]; st.markdown(f'**{aa}**'); st.caption(bb)
                        else: st.write(val)
                st.divider()

    with t3:
        rows=matched(return_rows)
        if not rows:
            _loan_empty('↩️','Không có yêu cầu trả đang chờ','Khi độc giả gửi yêu cầu trả sách, phiếu sẽ hiện tại đây.')
        else:
            for l in rows:
                with st.container(border=True):
                    a,b,c=st.columns([2,3,1.5])
                    with a: st.markdown(f"**{l.get('full_name') or '—'}**"); st.caption(f"{l.get('member_code') or ''} • Phiếu #{l['id']}")
                    with b: st.markdown(f"**{l.get('title') or '—'}**"); st.caption(f"Hạn trả: {l.get('due_date') or '—'} • Phạt tạm tính: {money(int(l.get('fine_amount') or 0))}")
                    with c:
                        if st.button('📥 Xác nhận trả',key=f'v21_confirm_{l["id"]}',type='primary',use_container_width=True):
                            ok,msg=db.confirm_return(l['id'],user['id']); (st.success if ok else st.error)(msg); st.rerun()

    with t4:
        a,b=st.columns([1,2.4])
        with a:
            fine_status=st.selectbox('Trạng thái',['Tất cả','unpaid','paid'],format_func=lambda x:'Tất cả' if x=='Tất cả' else status_vi(x),key='v21_fine_filter')
        fines=db.list_fines(fine_status)
        if q:
            k=q.strip().lower(); fines=[f for f in fines if k in ' '.join(str(f.get(x) or '').lower() for x in ('id','member_code','full_name','book_id','title','reason'))]
        if not fines:
            _loan_empty('💳','Không có khoản phạt','Các khoản quá hạn hoặc bồi thường sẽ được ghi nhận tại đây.')
        else:
            for f in fines:
                with st.container(border=True):
                    c1,c2,c3,c4=st.columns([1.7,2.6,1.2,1.5])
                    with c1: st.markdown(f"**{f.get('full_name') or '—'}**"); st.caption(f.get('member_code') or '')
                    with c2: st.markdown(f"**{f.get('title') or '—'}**"); st.caption(f.get('reason') or '')
                    with c3: st.markdown(f"**{money(int(f.get('amount') or 0))}**"); st.markdown(_loan_status_badge('returned' if f.get('status')=='paid' else 'overdue'),unsafe_allow_html=True)
                    with c4:
                        if f.get('status')=='unpaid':
                            if st.button('✓ Đã thu tiền',key=f'v21_pay_{f["id"]}',type='primary',use_container_width=True):
                                ok,msg=db.pay_fine(f['id'],user['id']); (st.success if ok else st.error)(msg); st.rerun()
                        else: st.success('Đã thanh toán')

    with t5:
        threshold=int(db.get_setting('lost_after_days',60))
        replacement_default=int(db.get_setting('lost_book_fee',150000))
        st.caption(f"Quy tắc: chỉ chuyển sang Không trả/Mất khi quá hạn tối thiểu {threshold} ngày • Phí thay thế mặc định: {money(replacement_default)}")

        eligible=[]
        from datetime import date as _date
        for r in overdue_rows:
            try:
                late=(_date.today()-_date.fromisoformat(r.get('due_date'))).days
            except Exception:
                late=0
            if late>=threshold:
                rr=dict(r); rr['_late_days']=late; eligible.append(rr)

        if eligible:
            with st.expander('⚠️ Xử lý phiếu quá hạn lâu ngày',expanded=False):
                oid=st.selectbox('Phiếu đủ điều kiện',[x['id'] for x in eligible],format_func=lambda x:next(f"#{r['id']} — {r['full_name']} — {r['title']} — quá hạn {r['_late_days']} ngày" for r in eligible if r['id']==x),key='v21_lost_pick')
                replacement=st.number_input('Phí thay thế sách (VNĐ)',0,10000000,replacement_default,step=10000,key='v21_lost_fee')
                if st.button('⚠️ Ghi nhận không trả / mất sách',type='primary',use_container_width=True,key='v21_mark_lost'):
                    ok,msg=db.mark_loan_lost(oid,user['id'],replacement); (st.success if ok else st.error)(msg); st.rerun()
        else:
            st.info(f'Hiện không có phiếu quá hạn từ {threshold} ngày trở lên cần chuyển sang trạng thái Không trả/Mất.')

        st.markdown('### Hồ sơ không trả / mất sách')
        lost=matched(lost_rows)
        if not lost:
            _loan_empty('🛡️','Không có hồ sơ chưa xử lý','Các trường hợp không trả hoặc mất sách sẽ xuất hiện tại đây.')
        else:
            fine_by_loan={int(f.get('loan_id')):f for f in fines_all if f.get('loan_id') is not None}
            for l in lost:
                f=fine_by_loan.get(int(l['id']))
                with st.container(border=True):
                    c1,c2,c3,c4=st.columns([1.8,2.8,1.4,1.7])
                    with c1:
                        st.markdown(f"**{l.get('full_name') or '—'}**"); st.caption(f"{l.get('member_code') or ''} • Phiếu #{l['id']}")
                    with c2:
                        st.markdown(f"**{l.get('title') or '—'}**"); st.caption(f"{l.get('book_id') or ''} • Hạn trả: {l.get('due_date') or '—'}")
                    with c3:
                        st.caption('NGHĨA VỤ'); st.markdown(f"**{money(int(l.get('fine_amount') or 0))}**"); st.markdown(_loan_status_badge('lost'),unsafe_allow_html=True)
                    with c4:
                        if f and f.get('status')=='unpaid':
                            if st.button('✓ Đã bồi thường',key=f'v21_lost_pay_{f["id"]}',type='primary',use_container_width=True):
                                ok,msg=db.pay_fine(f['id'],user['id']); (st.success if ok else st.error)(msg); st.rerun()
                        else:
                            st.success('Đã xử lý')
                    if l.get('note'): st.caption(l.get('note'))

def reservations_page(user):
    page_head('Đặt trước Sách','Theo dõi hàng chờ và xử lý yêu cầu đặt trước')
    a,b=st.columns([2,1])
    with a: q=st.text_input('Tìm kiếm đặt trước',placeholder='Độc giả, mã sách, tên sách...')
    with b: status=st.selectbox('Trạng thái',['Tất cả','pending','fulfilled','cancelled'],format_func=lambda x:'Tất cả' if x=='Tất cả' else status_vi(x))
    rows=db.list_reservations(status,q)
    if rows: st.dataframe(pd.DataFrame(rows)[['id','member_code','full_name','book_id','title','available','created_at','status','handled_at']],use_container_width=True,hide_index=True)
    pending=[r for r in rows if r['status']=='pending']
    if pending:
        rid=st.selectbox('Chọn phiếu đặt trước',[r['id'] for r in pending],format_func=lambda x:next(f"#{r['id']} — {r['full_name']} — {r['title']}" for r in pending if r['id']==x))
        note=st.text_input('Ghi chú xử lý',placeholder='Ví dụ: đã giữ sách tại quầy đến 25/09')
        c1,c2=st.columns(2)
        with c1:
            if st.button('✅ Đánh dấu đã xử lý',type='primary',use_container_width=True): ok,msg=db.update_reservation(rid,'fulfilled',note,user['id']);(st.success if ok else st.error)(msg);st.rerun()
        with c2:
            if st.button('❌ Hủy đặt trước',use_container_width=True): ok,msg=db.update_reservation(rid,'cancelled',note,user['id']);(st.success if ok else st.error)(msg);st.rerun()


def accounts_page(user):
    page_head('Tài khoản & Phân quyền','Quản lý vai trò, trạng thái và bảo mật tài khoản hệ thống')
    if user['role']!='admin': st.warning('Chỉ Quản trị viên Hệ thống được phép thay đổi phân quyền.'); return
    users=db.list_users()
    cols=st.columns(4)
    data=[('🛡️','Quản trị',sum(1 for x in users if x['role']=='admin')),('📚','Thủ thư',sum(1 for x in users if x['role']=='librarian')),('👤','Độc giả',sum(1 for x in users if x['role']=='reader')),('🔒','Đang khóa',sum(1 for x in users if x['status']=='locked'))]
    for col,(ico,label,val) in zip(cols,data):
        with col: st.markdown(f'<div class="admin-summary-card"><div class="admin-summary-label">{ico} {label}</div><div class="admin-summary-value">{val}</div></div>',unsafe_allow_html=True)
    st.write('')
    st.dataframe(pd.DataFrame(users)[['member_code','username','full_name','email','role','status','created_at']],use_container_width=True,hide_index=True,column_config={'role':'Vai trò','status':'Trạng thái'})
    t1,t2=st.tabs(['🔐 Quản lý & phân quyền','➕ Tạo tài khoản mới'])
    with t1:
        candidates=[u for u in users if u['id']!=user['id']]
        if not candidates: st.info('Chưa có tài khoản khác để quản lý.'); return
        target_id=st.selectbox('Chọn tài khoản',[u['id'] for u in candidates],format_func=lambda x:next(f"{u['username']} — {u['full_name']} ({role_name(u['role'])})" for u in users if u['id']==x))
        target=db.get_user(target_id); left,right=st.columns([1,1.35],gap='large')
        with left:
            cls='locked' if target['status']=='locked' else ''
            card_html=f"""<div class="reader-admin-card"><div class="reader-admin-code">@{html.escape(target['username'])}</div><div class="reader-admin-name">{html.escape(target['full_name'])}</div><div style="margin-top:9px"><span class="role-pill">{role_name(target['role'])}</span> <span class="status-pill {cls}">{status_vi(target['status'])}</span></div><div class="reader-admin-meta">📧 {html.escape(target.get('email') or '—')}<br>☎️ {html.escape(target.get('phone') or '—')}<br>🪪 {html.escape(target.get('member_code') or '—')}</div></div>"""
            st.markdown(card_html,unsafe_allow_html=True)
        with right:
            st.markdown('#### Quyền truy cập')
            new_role=st.selectbox('Vai trò',['reader','librarian','admin'],index=['reader','librarian','admin'].index(target['role']),format_func=role_name)
            c1,c2=st.columns(2)
            with c1:
                if st.button('💾 Lưu vai trò',type='primary',use_container_width=True): db.set_user_role(target_id,new_role);db.log_activity(user['id'],'Đổi phân quyền',f"{target['username']} -> {new_role}");st.success('Đã cập nhật vai trò.');st.rerun()
            with c2:
                new_status='locked' if target['status']=='active' else 'active'; label='🔒 Khóa tài khoản' if target['status']=='active' else '🔓 Mở khóa tài khoản'
                if st.button(label,use_container_width=True): db.set_user_status(target_id,new_status);db.log_activity(user['id'],'Đổi trạng thái tài khoản',target['username']);st.success('Đã cập nhật.');st.rerun()
            st.markdown('#### Bảo mật')
            reset=st.text_input('Mật khẩu mới',type='password',placeholder='Ít nhất 6 ký tự')
            if st.button('Đặt lại mật khẩu',use_container_width=True):
                if len(reset)<6: st.error('Mật khẩu cần ít nhất 6 ký tự.')
                else: db.update_password_hash(target_id,auth.hash_password(reset));db.log_activity(user['id'],'Đặt lại mật khẩu',target['username']);st.success('Đã đặt lại mật khẩu.')
    with t2:
        with st.form('create_account'):
            a,b=st.columns(2)
            with a: username=st.text_input('Tên đăng nhập'); name=st.text_input('Họ tên'); email=st.text_input('Email')
            with b: phone=st.text_input('Số điện thoại'); password=st.text_input('Mật khẩu',type='password'); role=st.selectbox('Vai trò',['reader','librarian','admin'],format_func=role_name)
            create=st.form_submit_button('Tạo tài khoản',type='primary')
        if create:
            if len(password)<6: st.error('Mật khẩu cần ít nhất 6 ký tự.')
            else:
                ok,msg=db.create_user(username,auth.hash_password(password),name,email,phone,role)
                if ok: db.log_activity(user['id'],'Tạo tài khoản',username)
                (st.success if ok else st.error)(msg); st.rerun()

def ai_recommend_page(user):
    page_head('Trợ lý AI & Gợi ý Sách','Chế độ mượt: streaming thời gian thực, tra cứu cục bộ trước, Gemini phân tích tổng quát')
    st.markdown('<div class="ai-fast-note">⚡ FAST CHAT STREAMING: Phản hồi từng chữ siêu mượt. Tra cứu sách/quy định phản hồi tức thì từ cache & MySQL; Gemini sinh câu trả lời trực tiếp.</div>',unsafe_allow_html=True)
    left,right=st.columns([1.65,1],gap='large')
    with left:
        ai=get_ai_service()
        top=st.columns(3)
        prompts=['📖 Sách về tình yêu','💻 Gợi ý sách Python','📋 Quy định mượn tối đa']
        for col,prompt in zip(top,prompts):
            with col:
                if st.button(prompt,use_container_width=True,key='aiquick_'+prompt): st.session_state['ai_quick_prompt']=prompt
        if st.button('🧹 Xóa cuộc trò chuyện',key='clear_ai_chat'):
            st.session_state.chat_messages=[{'role':'assistant','content':'Xin chào! Mình là Trợ lý SmartLibrary AI. Bạn muốn tìm sách hay hỏi kiến thức gì?'}]
            st.session_state.pop('last_rag_info',None)
            st.rerun()

        # Khung hội thoại AI nhỏ gọn có thanh cuộn riêng để xem lại câu hỏi
        chat_box = st.container(height=480)
        with chat_box:
            for m in st.session_state.chat_messages:
                with st.chat_message(m['role']):
                    st.markdown(m['content'])

        q=st.chat_input('Hỏi về sách, quy định thư viện, học tập, lập trình...')
        q=q or st.session_state.pop('ai_quick_prompt',None)
        if q:
            st.session_state.chat_messages.append({'role':'user','content':q})
            with chat_box:
                with st.chat_message('user'):
                    st.markdown(q)
                rag=ai.retrieve(q)
                st.session_state['last_rag_info']=ai.route_info(rag=rag)
                with st.chat_message('assistant'):
                    answer=st.write_stream(ai.answer_stream(q,st.session_state.chat_messages[:-1],rag=rag))
            st.session_state.chat_messages.append({'role':'assistant','content':answer})
            st.rerun()
        if st.session_state.get('last_rag_info'):
            info=st.session_state['last_rag_info']
            with st.expander('🧠 Chi tiết truy xuất RAG (Báo cáo kỹ thuật)'):
                route_badge={'BOOK':'📘 THƯ VIỆN SÁCH','POLICY':'📜 CHÍNH SÁCH','GENERAL':'🌐 KHIẾN THỨC TỔNG QUÁT'}.get(info['route'], info['route'])
                st.write(f"**Nhánh xử lý:** `{route_badge}`")
                st.write(f"**Sách truy xuất từ MySQL:** {', '.join(info['retrieved_books']) or 'Không có'}")
                st.caption(f"BM25 Book Score: {info['book_score']} • Policy Score: {info['policy_score']} • Chunks: {info['policy_chunks']}")
    with right:
        st.markdown('<div class="panel"><div class="mini-title">✨ Sách gợi ý nhanh</div>',unsafe_allow_html=True)
        topic=st.selectbox('Chủ đề',['Công nghệ thông tin','Trinh thám','Tình cảm','Kỹ năng sống','Tâm lý học','Kinh tế & Kinh doanh'])
        recs=db.list_books(category=topic,only_available=True)[:5]
        if recs:
            for r in recs: st.write(f"📘 **{r['title']}**"); st.caption(f"{r['author']} • còn {r['available']} bản")
        else: st.caption('Chưa có sách còn bản ở chủ đề này.')
        st.markdown('</div>',unsafe_allow_html=True)
        info=db.connection_info(); ok_db,msg=db.test_connection()
        with st.expander('🧩 Kỹ thuật hệ thống'):
            tech=f"""- **Frontend:** Streamlit + CSS tùy biến.
- **Database:** **{info['engine'].upper()}** — `{info['database']}` tại `{info['host']}:{info['port']}`.
- **Tìm kiếm:** BM25 có mở rộng từ khóa theo ngữ nghĩa/thể loại.
- **RAG tự chọn:** BOOK / POLICY / GENERAL.
- **Tối ưu tốc độ:** BOOK và POLICY trả lời cục bộ; không gọi Gemini nếu không cần.
- **Generation:** Gemini chỉ xử lý kiến thức tổng quát hoặc yêu cầu phân tích/tóm tắt.
- **Trạng thái DB:** {'✅ Đã kết nối' if ok_db else '❌ Chưa kết nối'}.
"""
            st.markdown(tech)

def reports_page(user):
    page_head('Báo cáo & Xuất dữ liệu', 'Xuất dữ liệu Excel/CSV và tạo báo cáo in ấn chính thức')
    snap = db.report_snapshot()
    stats, cats, months = db.admin_stats()

    # --- TOP ROW CARDS (3 Columns) ---
    c1, c2, c3 = st.columns(3, gap='large')

    with c1:
        st.markdown('''
        <div class="export-card">
          <div>
            <div class="export-card-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14 2H6C4.89 2 4 2.89 4 4V20C4 21.11 4.89 22 6 22H18C19.11 22 20 21.11 20 20V8L14 2Z" fill="#1e293b"/>
                <path d="M14 2V8H20" fill="#475569"/>
                <path d="M9.5 12.5L14.5 17.5M14.5 12.5L9.5 17.5" stroke="#10b981" stroke-width="2.5" stroke-linecap="round"/>
              </svg>
            </div>
            <div class="export-card-title">Xuất Danh sách Sách (Excel / CSV)</div>
            <div class="export-card-desc">Tải xuống toàn bộ kho sách bao gồm tên, tác giả, thể loại, số lượng tồn kho và vị trí kệ.</div>
          </div>
        ''', unsafe_allow_html=True)
        st.download_button(
            '📥 Xuất Excel Sách',
            csv_bytes(snap['books']),
            file_name='danh_sach_sach.csv',
            mime='text/csv',
            use_container_width=True,
            key='exp_books_btn'
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with c2:
        st.markdown('''
        <div class="export-card">
          <div>
            <div class="export-card-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14 2H6C4.89 2 4 2.89 4 4V20C4 21.11 4.89 22 6 22H18C19.11 22 20 21.11 20 20V8L14 2Z" fill="#1e293b"/>
                <path d="M14 2V8H20" fill="#475569"/>
                <text x="6" y="16" fill="#06b6d4" font-size="6.5" font-weight="900" font-family="sans-serif">CSV</text>
              </svg>
            </div>
            <div class="export-card-title">Xuất Danh sách Độc giả</div>
            <div class="export-card-desc">Tải danh sách độc giả, loại thẻ, ngày hết hạn và trạng thái hoạt động dưới dạng file CSV.</div>
          </div>
        ''', unsafe_allow_html=True)
        st.download_button(
            '📥 Xuất Danh sách Độc giả',
            csv_bytes(snap['users']),
            file_name='danh_sach_doc_gia.csv',
            mime='text/csv',
            use_container_width=True,
            key='exp_readers_btn'
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with c3:
        st.markdown('''
        <div class="export-card">
          <div>
            <div class="export-card-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M14 2H6C4.89 2 4 2.89 4 4V20C4 21.11 4.89 22 6 22H18C19.11 22 20 21.11 20 20V8L14 2Z" fill="#1e293b"/>
                <path d="M14 2V8H20" fill="#475569"/>
                <path d="M8 12H16M8 15H16M8 18H13" stroke="#f59e0b" stroke-width="2.2" stroke-linecap="round"/>
              </svg>
            </div>
            <div class="export-card-title">Xuất Nhật ký Mượn / Trả & Phạt</div>
            <div class="export-card-desc">Xuất toàn bộ báo cáo lịch sử mượn trả, ngày quá hạn và tiền phạt đã thu.</div>
          </div>
        ''', unsafe_allow_html=True)
        st.download_button(
            '📥 Xuất Báo cáo Mượn Trả',
            csv_bytes(snap['loans']),
            file_name='nhat_ky_muon_tra.csv',
            mime='text/csv',
            use_container_width=True,
            key='exp_loans_btn'
        )
        st.markdown('</div>', unsafe_allow_html=True)

    st.write('')

    # --- SECOND ROW CARDS (3 Columns) ---
    c4, c5, c6 = st.columns(3, gap='large')

    with c4:
        st.markdown('''
        <div class="export-card">
          <div>
            <div class="export-card-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M19 8H5C3.34 8 2 9.34 2 11V17H6V21H18V17H22V11C22 9.34 20.66 8 19 8Z" fill="#1e293b"/>
                <path d="M6 3H18V8H6V3Z" fill="#4f46e5"/>
                <circle cx="18" cy="11.5" r="1.2" fill="#10b981"/>
              </svg>
            </div>
            <div class="export-card-title">In Báo cáo Thư viện Tổng hợp</div>
            <div class="export-card-desc">Tạo trang báo cáo hoàn chỉnh có định dạng chuẩn in ấn để nộp ban giám hiệu / ban quản lý.</div>
          </div>
        ''', unsafe_allow_html=True)
        if st.button('🖨️ Xem & In Báo cáo', key='exp_print_btn', use_container_width=True):
            st.session_state.show_print_report = not st.session_state.get('show_print_report', False)
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with c5:
        st.markdown('''
        <div class="export-card">
          <div>
            <div class="export-card-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <path d="M17 3H7C5.9 3 5 3.9 5 5V21L12 18L19 21V5C19 3.9 18.1 3 17 3Z" fill="#1e293b"/>
                <path d="M12 7V13M9 10H15" stroke="#8b5cf6" stroke-width="2.2" stroke-linecap="round"/>
              </svg>
            </div>
            <div class="export-card-title">Xuất Phiếu Đặt trước Sách</div>
            <div class="export-card-desc">Xuất danh sách các lượt độc giả đặt trước sách đang chờ giữ chỗ tại thư viện.</div>
          </div>
        ''', unsafe_allow_html=True)
        st.download_button(
            '📥 Xuất Phiếu Đặt trước',
            csv_bytes(snap['reservations']),
            file_name='phieu_dat_truoc.csv',
            mime='text/csv',
            use_container_width=True,
            key='exp_res_btn'
        )
        st.markdown('</div>', unsafe_allow_html=True)

    with c6:
        st.markdown('''
        <div class="export-card">
          <div>
            <div class="export-card-icon">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="12" cy="12" r="10" fill="#1e293b"/>
                <path d="M12 6V18M9 9H13.5C14.33 9 15 9.67 15 10.5C15 11.33 14.33 12 13.5 12H10.5C9.67 12 9 12.67 9 13.5C9 14.33 9.67 15 10.5 15H15" stroke="#ef4444" stroke-width="2" stroke-linecap="round"/>
              </svg>
            </div>
            <div class="export-card-title">Xuất Báo cáo Tiền phạt</div>
            <div class="export-card-desc">Báo cáo thu tiền phạt quá hạn và các khoản đền bù mất sách chưa thu.</div>
          </div>
        ''', unsafe_allow_html=True)
        st.download_button(
            '📥 Xuất Báo cáo Tiền phạt',
            csv_bytes(snap['fines']),
            file_name='bao_cao_tien_phat.csv',
            mime='text/csv',
            use_container_width=True,
            key='exp_fines_btn'
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # --- PRINTABLE REPORT MODAL / EXPANDER ---
    if st.session_state.get('show_print_report'):
        st.write('')
        with st.container(border=True):
            st.markdown('''
            <div style="text-align:center;padding:20px;background:linear-gradient(135deg,#f8fafc,#eff6ff);border-radius:16px;margin-bottom:16px;border:1px solid #cbd5e1">
              <h3 style="margin:0;color:#1e293b;font-weight:800">CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM</h3>
              <p style="margin:4px 0 12px;font-weight:700;color:#475569">Độc lập - Tự do - Hạnh phúc</p>
              <h2 style="margin:16px 0 4px;color:#4f46e5;font-weight:900">BÁO CÁO THỐNG KÊ HOẠT ĐỘNG THƯ VIỆN TỔNG HỢP</h2>
              <p style="color:#64748b;font-size:0.9rem">Hệ thống SmartLibrary AI • Cập nhật dữ liệu thời gian thực</p>
            </div>
            ''', unsafe_allow_html=True)

            m1, m2, m3, m4 = st.columns(4)
            m1.metric('Tổng lượt mượn', len(snap['loans']))
            m2.metric('Tiền phạt chưa thu', money(stats['unpaid_fines']))
            m3.metric('Phiếu đặt trước', len(snap['reservations']))
            m4.metric('Đầu sách sẵn sàng', stats['available'])

            st.write('---')
            st.subheader('📌 Bảng dữ liệu mượn/trả gần nhất')
            if snap['loans']:
                st.dataframe(pd.DataFrame(snap['loans']), use_container_width=True, hide_index=True)

            b1, b2 = st.columns([1.2, 4])
            with b1:
                if st.button('🖨️ Thực hiện In Báo cáo', key='trigger_print', type='primary', use_container_width=True):
                    st.components.v1.html("<script>window.print();</script>", height=0)
            with b2:
                if st.button('✕ Đóng trang báo cáo in', key='close_print_report', use_container_width=True):
                    st.session_state.show_print_report = False
                    st.rerun()

    # --- ANALYTICS CHARTS BELOW CARDS ---
    st.write('')
    st.divider()
    x, y = st.columns(2, gap='large')
    with x:
        st.markdown('### 📈 Mượn theo tháng')
        if months:
            st.bar_chart(pd.DataFrame(months).set_index('month')['total'], height=240)
    with y:
        st.markdown('### 📊 Cơ cấu kho sách')
        if cats:
            st.bar_chart(pd.DataFrame(cats[:10]).set_index('category')['copies'], height=240)

    st.subheader('📋 Xem trước Bảng dữ liệu mượn/trả')
    if snap['loans']:
        st.dataframe(pd.DataFrame(snap['loans']), use_container_width=True, hide_index=True)


def settings_page(user):
    page_head('Cài đặt','Thiết lập quy định và thông tin thư viện')
    info=db.connection_info(); ok_db,msg_db=db.test_connection()
    with st.container(border=True):
        c1,c2,c3,c4=st.columns(4)
        c1.metric('Database',info['engine'].upper()); c2.metric('Máy chủ',str(info['host'])); c3.metric('Cổng',str(info['port'] or '—')); c4.metric('CSDL',str(info['database']))
        if ok_db and info['engine']=='mysql': st.success('✅ MySQL đã kết nối và đang được hệ thống sử dụng.')
        elif ok_db: st.success('✅ Database đang hoạt động.')
        else: st.error(msg_db)
    with st.form('settings_form'):
        a,b=st.columns(2)
        with a:
            name=st.text_input('Tên thư viện',db.get_setting('library_name','SmartLibrary AI'))
            days=st.number_input('Số ngày mượn',1,180,int(db.get_setting('loan_days',14)))
            maxb=st.number_input('Số sách tối đa / độc giả',1,50,int(db.get_setting('max_books_per_reader',5)))
            renew=st.number_input('Số lần gia hạn tối đa',0,10,int(db.get_setting('max_renewals',2)))
        with b:
            fine=st.number_input('Phí quá hạn / ngày (VNĐ)',0,1000000,int(db.get_setting('fine_per_day',5000)),step=1000)
            lockdays=st.number_input('Tự khóa quyền mượn sau quá hạn (ngày)',1,365,int(db.get_setting('auto_lock_overdue_days',30)))
            lostdays=st.number_input('Ngưỡng xử lý không trả/mất (ngày)',1,730,int(db.get_setting('lost_after_days',60)))
            lostfee=st.number_input('Phí thay thế sách mặc định (VNĐ)',0,10000000,int(db.get_setting('lost_book_fee',150000)),step=10000)
            hold=st.number_input('Số ngày giữ sách đặt trước',1,30,int(db.get_setting('reservation_hold_days',3)))
            email=st.text_input('Email thư viện',db.get_setting('library_email','library@ictu.edu.vn'))
            phone=st.text_input('Điện thoại thư viện',db.get_setting('library_phone','0966320627'))
        st.markdown('**Cấu hình RAG / tìm kiếm**')
        r1,r2=st.columns(2)
        with r1: ragk=st.number_input('Top-K ngữ cảnh RAG',1,20,int(db.get_setting('rag_top_k',5)))
        with r2: ragmode=st.selectbox('Chế độ RAG',['auto'],index=0,help='Auto tự chọn dữ liệu sách, chính sách hoặc kiến thức tổng quát.')
        save=st.form_submit_button('Lưu cài đặt',type='primary')
    if save:
        for k,v in [('library_name',name),('loan_days',days),('max_books_per_reader',maxb),('max_renewals',renew),('fine_per_day',fine),('auto_lock_overdue_days',lockdays),('lost_after_days',lostdays),('lost_book_fee',lostfee),('reservation_hold_days',hold),('rag_top_k',ragk),('rag_mode',ragmode),('library_email',email),('library_phone',phone)]: db.set_setting(k,v)
        db.log_activity(user['id'],'Cập nhật cài đặt','Thay đổi quy định thư viện'); st.success('Đã lưu cài đặt.')
    with st.expander('📐 Luồng xử lý mới của hệ thống'):
        st.markdown('''
**Giới hạn mượn:** kiểm tra hạn mức ngay khi độc giả gửi yêu cầu và kiểm tra lại khi thủ thư duyệt.  
**Không trả sách:** quá hạn → tính phạt → chặn mượn mới → đủ số ngày cấu hình thì tự khóa quyền mượn → quản trị có thể đánh dấu chưa trả/mất và cộng phí thay thế.  
**BM25:** dùng để xếp hạng kết quả tìm kiếm theo từ khóa thay vì chỉ `LIKE`.  
**RAG tự chọn:** câu hỏi về sách → truy xuất sách; câu hỏi quy định → truy xuất chính sách; câu hỏi tổng quát → Gemini trực tiếp.
''')

# ------------------------------------------------------------------
# READER MEMBER PORTAL PAGES
# ------------------------------------------------------------------
def reader_cover_html(book):
    cp=cover(book)
    if cp:
        return f'<img class="reader-book-cover" src="{static_url(book.get("cover_image"))}" loading="lazy" decoding="async" alt="{html.escape(book.get("title", "Sách"))}">'
    return '<div class="reader-book-cover" style="display:flex;align-items:center;justify-content:center;font-size:2rem">📖</div>'


def reader_member_home(user):
    st.markdown('<div class="reader-theme-marker"></div>',unsafe_allow_html=True)
    s=db.reader_stats(user['id']); ach=db.reader_achievement_stats(user['id']); current=db.get_user(user['id']); limit_state=db.reader_borrow_limit_status(user['id'])
    st.markdown(f'<div class="reader-top-card"><div class="reader-welcome">Xin chào, {html.escape(current["full_name"])} 👋</div><div class="reader-muted">Đây là không gian hội viên của bạn. Theo dõi sách, yêu cầu mượn và hoạt động đọc tại một nơi.</div><div style="margin-top:11px"><span class="reader-chip">HỘI VIÊN</span><span class="reader-chip">{html.escape(current.get("card_type") or "Độc giả")}</span><span class="reader-chip">Hạn mức: {limit_state["active"]}/{limit_state["limit"]} sách</span></div></div>',unsafe_allow_html=True)
    cols=st.columns(4)
    data=[('📖 Đang đọc',s['borrowed']),('✅ Đã hoàn thành',ach['returned']),('❤️ Yêu thích',ach['favorites']),('🔖 Đặt trước',ach['reservations'])]
    for c,(lab,val) in zip(cols,data):
        with c: st.markdown(f'<div class="reader-stat"><div class="reader-stat-label">{lab}</div><div class="reader-stat-value">{val}</div></div>',unsafe_allow_html=True)
    st.write('')
    a,b=st.columns([1.65,1],gap='large')
    with a:
        st.markdown('<div class="reader-panel"><div class="reader-panel-title">📚 Đang đọc / đang mượn</div>',unsafe_allow_html=True)
        loans=[x for x in db.reader_loans(user['id']) if x['status'] in ('borrowed','overdue','return_requested')][:4]
        if loans:
            for l in loans:
                st.markdown(f'<div class="reader-history-row"><div class="reader-status">{status_vi(l["status"])}</div><div><b>{html.escape(l["title"])}</b><div class="reader-muted">{html.escape(l["author"])}</div></div><div>Hạn {l.get("due_date") or "—"}</div><div>{money(l.get("fine_amount"))}</div></div>',unsafe_allow_html=True)
        else:
            st.markdown('<div class="reader-empty"><div class="reader-empty-icon">▱⌕</div><div class="reader-empty-title">Chưa có cuốn sách nào đang đọc</div><div class="reader-empty-sub">Khám phá kho sách và gửi yêu cầu mượn ngay.</div></div>',unsafe_allow_html=True)
        st.markdown('</div>',unsafe_allow_html=True)
    with b:
        st.markdown('<div class="reader-panel"><div class="reader-panel-title">🏆 Thành tích đọc</div>',unsafe_allow_html=True)
        st.metric('Sách đã hoàn thành',ach['returned']); st.metric('Sách yêu thích',ach['favorites']); st.metric('Lượt đặt trước',ach['reservations'])
        if st.button('Xem thành tích',key='reader_home_ach',use_container_width=True): st.session_state.nav_page='Thành tích';st.rerun()
        st.markdown('</div>',unsafe_allow_html=True)
    st.markdown('<div class="reader-panel"><div class="reader-panel-title">🔥 Top sách được quan tâm</div>',unsafe_allow_html=True)
    books=db.top_borrowed_books(5); cols=st.columns(5)
    for col,bk in zip(cols,books):
        with col:
            st.markdown(f'<div class="reader-book-card">{reader_cover_html(bk)}<div class="reader-book-title">{html.escape(bk["title"])}</div><div class="reader-book-meta">{html.escape(bk["author"])} · {html.escape(bk["category"])}</div></div>',unsafe_allow_html=True)
            if st.button('Xem sách',key=f'mhome_{bk["id"]}',use_container_width=True):
                db.increment_book_view(bk['id']); st.session_state.reader_detail=bk['id']; st.session_state.nav_page='Tủ sách cá nhân'; st.rerun()
    st.markdown('</div>',unsafe_allow_html=True)


def reader_account_page(user):
    st.markdown('<div class="reader-theme-marker"></div>',unsafe_allow_html=True)
    current=db.get_user(user['id']); page_head('Quản lý thông tin','Thông tin cá nhân, địa chỉ và bảo mật tài khoản')
    tabs=st.tabs(['Thông tin cá nhân','Địa chỉ','Tài khoản và bảo mật','Tài khoản liên kết'])
    with tabs[0]:
        a,b=st.columns([1.5,.8],gap='large')
        with a:
            with st.form('reader_personal_info'):
                st.text_input('Tên đăng nhập',current['username'],disabled=True)
                st.text_input('ID người dùng',str(current['id']),disabled=True)
                name=st.text_input('Họ và tên',current['full_name']); birth=st.text_input('Ngày sinh',current.get('birth_date') or '',placeholder='YYYY-MM-DD')
                gender=st.selectbox('Giới tính',['','Nữ','Nam','Khác'],index=['','Nữ','Nam','Khác'].index(current.get('gender') or '') if (current.get('gender') or '') in ['','Nữ','Nam','Khác'] else 0)
                save=st.form_submit_button('Cập nhật',type='primary')
            if save:
                db.update_reader_profile(current['id'],name,current.get('email') or '',current.get('phone') or '',birth,gender,current.get('address') or '')
                st.session_state.user=db.get_user(current['id']);st.success('Đã cập nhật thông tin.');st.rerun()
        with b:
            st.markdown('<div class="reader-profile-box" style="text-align:center"><div class="reader-avatar">👤</div><div style="margin-top:10px;font-weight:900">Ảnh đại diện</div><div class="reader-muted" style="margin-top:5px">Phiên bản demo dùng avatar mặc định.</div></div>',unsafe_allow_html=True)
    with tabs[1]:
        with st.form('reader_address'):
            address=st.text_area('Địa chỉ',current.get('address') or '',height=120)
            phone=st.text_input('Số điện thoại',current.get('phone') or '');email=st.text_input('Email',current.get('email') or '')
            save2=st.form_submit_button('Lưu địa chỉ',type='primary')
        if save2:
            db.update_reader_profile(current['id'],current['full_name'],email,phone,current.get('birth_date') or '',current.get('gender') or '',address);st.success('Đã lưu địa chỉ.');st.rerun()
    with tabs[2]:
        st.markdown('<div class="reader-security-card"><b>Tên đăng nhập</b><br><span class="reader-muted">'+html.escape(current['username'])+'</span></div>',unsafe_allow_html=True)
        with st.form('reader_password_change'):
            old=st.text_input('Mật khẩu hiện tại',type='password');new=st.text_input('Mật khẩu mới',type='password');new2=st.text_input('Nhập lại mật khẩu',type='password');change=st.form_submit_button('Đổi mật khẩu',type='primary')
        if change:
            ok,_,_=auth.authenticate(current['username'],old)
            if not ok: st.error('Mật khẩu hiện tại không đúng.')
            elif len(new)<6: st.error('Mật khẩu mới cần ít nhất 6 ký tự.')
            elif new!=new2: st.error('Mật khẩu nhập lại không khớp.')
            else: db.update_password_hash(current['id'],auth.hash_password(new));st.success('Đã đổi mật khẩu.')
    with tabs[3]:
        st.markdown('<div class="reader-security-card">Google <span style="float:right;color:#9ea2a8">Chưa liên kết</span></div><div class="reader-security-card">Facebook <span style="float:right;color:#9ea2a8">Chưa liên kết</span></div>',unsafe_allow_html=True)


def reader_shelf_page(user):
    st.markdown('<div class="reader-theme-marker"></div>',unsafe_allow_html=True)
    page_head('Tủ sách cá nhân','Sách đang đọc, lịch sử mượn và danh sách yêu thích')
    tabs=st.tabs(['Đang đọc','Đã đọc / Đã trả','Yêu thích','Khám phá sách'])
    loans=db.reader_loans(user['id'])
    with tabs[0]:
        rows=[x for x in loans if x['status'] in ('borrowed','overdue','return_requested')]
        if not rows: st.markdown('<div class="reader-empty"><div class="reader-empty-icon">▱⌕</div><div class="reader-empty-title">Chưa có cuốn sách nào</div><div class="reader-empty-sub">Cùng khám phá kho tàng tri thức của thư viện.</div></div>',unsafe_allow_html=True)
        for l in rows:
            with st.container(border=True):
                a,b,c=st.columns([2,1,1]);a.markdown(f'**{l["title"]}**');a.caption(l['author']);b.write(status_vi(l['status']));b.caption(f'Hạn: {l.get("due_date") or "—"}')
                with c:
                    if l['status']=='borrowed' and st.button('Gia hạn',key=f'rsrenew_{l["id"]}',use_container_width=True): ok,msg=db.renew_loan(user['id'],l['id']);(st.success if ok else st.error)(msg);st.rerun()
                    if l['status'] in ('borrowed','overdue') and st.button('Yêu cầu trả',key=f'rsret_{l["id"]}',use_container_width=True): ok,msg=db.request_return(user['id'],l['id']);(st.success if ok else st.error)(msg);st.rerun()
    with tabs[1]:
        rows=[x for x in loans if x['status']=='returned']
        if rows: st.dataframe(pd.DataFrame(rows)[['book_id','title','author','returned_date','fine_amount']],use_container_width=True,hide_index=True)
        else: st.info('Chưa có lịch sử sách đã trả.')
    with tabs[2]:
        favs=db.list_favorites(user['id'])
        if not favs: st.info('Bạn chưa thêm sách yêu thích.')
        for i in range(0,len(favs),4):
            cols=st.columns(4)
            for j,bk in enumerate(favs[i:i+4]):
                with cols[j]:
                    st.markdown(f'<div class="reader-book-card">{reader_cover_html(bk)}<div class="reader-book-title">{html.escape(bk["title"])}</div><div class="reader-book-meta">{html.escape(bk["author"])}</div></div>',unsafe_allow_html=True)
                    if st.button('Bỏ yêu thích',key=f'unfav_{bk["id"]}',use_container_width=True): db.toggle_favorite(user['id'],bk['id']);st.rerun()
    with tabs[3]:
        q=st.text_input('Tìm sách',placeholder='Tên sách, tác giả, thể loại...');books=db.list_books(q)[:20]
        if q: st.caption('🔎 Tìm theo từ khóa bằng BM25.')
        for i in range(0,len(books),4):
            cols=st.columns(4)
            for j,bk in enumerate(books[i:i+4]):
                with cols[j]:
                    st.markdown(f'<div class="reader-book-card">{reader_cover_html(bk)}<div class="reader-book-title">{html.escape(bk["title"])}</div><div class="reader-book-meta">{html.escape(bk["author"])} · còn {bk["available"]}</div></div>',unsafe_allow_html=True)
                    x,y=st.columns(2)
                    with x:
                        if st.button('Mượn',key=f'rsborrow_{bk["id"]}',use_container_width=True): ok,msg=db.request_borrow(user['id'],bk['id']);(st.success if ok else st.error)(msg)
                    with y:
                        fav=db.is_favorite(user['id'],bk['id'])
                        if st.button('♥' if fav else '♡',key=f'rsfav_{bk["id"]}',use_container_width=True): db.toggle_favorite(user['id'],bk['id']);st.rerun()


def reader_orders_page(user):
    st.markdown('<div class="reader-theme-marker"></div>',unsafe_allow_html=True)
    page_head('Quản lý đơn hàng','Theo dõi toàn bộ yêu cầu mượn, trả và đặt trước')
    rows=db.reader_loans(user['id']); res=db.reader_reservations(user['id'])
    tabs=st.tabs(['Tất cả','Chờ xác nhận','Đang mượn','Đã trả','Đã hủy','Đặt trước'])
    def show_loans(data):
        if not data: st.markdown('<div class="reader-empty"><div class="reader-empty-icon">✕</div><div class="reader-empty-title">Chưa có đơn nào</div><div class="reader-empty-sub">Các yêu cầu mượn/trả của bạn sẽ hiển thị tại đây.</div></div>',unsafe_allow_html=True);return
        for l in data:
            st.markdown(f'<div class="reader-history-row"><div>#{l["id"]}</div><div><b>{html.escape(l["title"])}</b><div class="reader-muted">{html.escape(l["author"])}</div></div><div class="reader-status">{status_vi(l["status"])}</div><div>{l.get("request_date") or "—"}</div></div>',unsafe_allow_html=True)
    with tabs[0]: show_loans(rows)
    with tabs[1]: show_loans([x for x in rows if x['status']=='pending'])
    with tabs[2]: show_loans([x for x in rows if x['status'] in ('borrowed','overdue','return_requested')])
    with tabs[3]: show_loans([x for x in rows if x['status']=='returned'])
    with tabs[4]: show_loans([x for x in rows if x['status']=='rejected'])
    with tabs[5]:
        if res: st.dataframe(pd.DataFrame(res)[['id','book_id','title','created_at','status']],use_container_width=True,hide_index=True)
        else: st.info('Chưa có sách đặt trước.')


def reader_achievements_page(user):
    st.markdown('<div class="reader-theme-marker"></div>',unsafe_allow_html=True)
    page_head('Thành tích','Theo dõi tiến độ và các cột mốc đọc sách')
    a=db.reader_achievement_stats(user['id']); cols=st.columns(4)
    vals=[('📚','Sách hoàn thành',a['returned']),('📖','Đang đọc',a['borrowed']),('❤️','Yêu thích',a['favorites']),('🔖','Đặt trước',a['reservations'])]
    for col,(ico,title,val) in zip(cols,vals):
        with col: st.markdown(f'<div class="reader-achievement"><div class="reader-ach-icon">{ico}</div><div class="reader-ach-title">{title}</div><div class="reader-stat-value">{val}</div></div>',unsafe_allow_html=True)
    st.write(''); st.markdown('<div class="reader-panel"><div class="reader-panel-title">🏅 Huy hiệu của bạn</div>',unsafe_allow_html=True)
    badges=[('🌱','Khởi đầu','Hoàn thành cuốn sách đầu tiên',a['returned']>=1),('📚','Mọt sách','Hoàn thành 5 cuốn sách',a['returned']>=5),('🔥','Đam mê đọc','Hoàn thành 10 cuốn sách',a['returned']>=10),('❤️','Nhà sưu tầm','Thêm 5 sách yêu thích',a['favorites']>=5)]
    cols=st.columns(4)
    for col,(ico,title,desc,earned) in zip(cols,badges):
        with col: st.markdown(f'<div class="reader-achievement" style="opacity:{1 if earned else .45}"><div class="reader-ach-icon">{ico}</div><div class="reader-ach-title">{title}</div><div class="reader-ach-desc">{desc}</div><div style="margin-top:8px;color:{"#19c99b" if earned else "#8c8e92"};font-size:.72rem;font-weight:850">{"Đã đạt" if earned else "Chưa đạt"}</div></div>',unsafe_allow_html=True)
    st.markdown('</div>',unsafe_allow_html=True)


def reader_transactions_page(user):
    st.markdown('<div class="reader-theme-marker"></div>',unsafe_allow_html=True)
    page_head('Lịch sử giao dịch','Nhật ký thao tác và tiền phạt của tài khoản')
    rows=db.reader_transactions(user['id'])
    tabs=st.tabs(['Tất cả','Hoạt động','Tiền phạt'])
    def show(data):
        if not data: st.markdown('<div class="reader-empty"><div class="reader-empty-icon">☷</div><div class="reader-empty-title">Bạn chưa có giao dịch nào</div><div class="reader-empty-sub">Thông tin hoạt động của tài khoản sẽ hiển thị tại đây.</div></div>',unsafe_allow_html=True);return
        for x in data:
            amount=money(x.get('amount')) if x.get('amount') else '—'
            st.markdown(f'<div class="reader-history-row"><div>{html.escape(x.get("kind") or "")}</div><div><b>{html.escape(x.get("title") or "")}</b><div class="reader-muted">{html.escape(x.get("detail") or "")}</div></div><div>{amount}</div><div>{html.escape(x.get("created_at") or "")}</div></div>',unsafe_allow_html=True)
    with tabs[0]: show(rows)
    with tabs[1]: show([x for x in rows if x['kind']=='activity'])
    with tabs[2]: show([x for x in rows if x['kind']=='fine'])


def reader_support_page(user):
    st.markdown('<div class="reader-theme-marker"></div>',unsafe_allow_html=True)
    page_head('Hỗ trợ khách hàng','Gửi yêu cầu hỗ trợ tới thư viện')
    a,b=st.columns([1.2,1],gap='large')
    with a:
        with st.form('support_form'):
            subject=st.selectbox('Chủ đề',['Đăng nhập / tài khoản','Mượn / trả sách','Tiền phạt','Đặt trước sách','Trợ lý AI','Khác'])
            content=st.text_area('Nội dung cần hỗ trợ',height=170,placeholder='Mô tả vấn đề của bạn...')
            send=st.form_submit_button('Gửi yêu cầu',type='primary')
        if send:
            if not content.strip(): st.error('Vui lòng nhập nội dung.')
            else:
                tid=db.add_support_ticket(user['id'],subject,content);db.log_activity(user['id'],'Gửi yêu cầu hỗ trợ',f'#{tid} {subject}');st.success(f'Đã gửi yêu cầu #{tid}.');st.rerun()
    with b:
        st.markdown('<div class="reader-panel"><div class="reader-panel-title">Thông tin hỗ trợ</div><div class="reader-muted">📧 library@ictu.edu.vn<br><br>☎ 0966320627<br><br>⏱ 08:00–17:00, Thứ 2–Thứ 6</div></div>',unsafe_allow_html=True)
    st.subheader('Yêu cầu đã gửi')
    tickets=db.list_support_tickets(user['id'])
    for t in tickets:
        st.markdown(f'<div class="reader-support-item"><div class="reader-support-title">#{t["id"]} · {html.escape(t["subject"])}</div><div class="reader-support-meta">{html.escape(t["content"])}<br>{html.escape(t["created_at"])} · Trạng thái: {html.escape(t["status"])}</div></div>',unsafe_allow_html=True)
    if not tickets: st.caption('Chưa có yêu cầu hỗ trợ.')


def reader_ai(user):
    st.markdown('<div class="reader-theme-marker"></div>',unsafe_allow_html=True)
    ai_recommend_page(user)

# ------------------------------------------------------------------
# ROUTER
# ------------------------------------------------------------------
if not st.session_state.user:
    render_public(); st.stop()

user=st.session_state.user
sidebar(user)
if user['role'] not in ('admin','librarian'):
    st.markdown('<div class="reader-theme-marker"></div>',unsafe_allow_html=True)
app_header(user)
page=st.session_state.nav_page

if user['role'] in ('admin','librarian'):
    if page=='Trang chủ': staff_home(user)
    elif page=='Tổng quan & Thống kê': dashboard_page(user)
    elif page=='Tra cứu & Quản lý Sách': books_page(user)
    elif page=='Quản lý Độc giả': readers_page(user)
    elif page=='Quản lý Mượn / Trả / Phạt': loans_fines_page(user)
    elif page=='Đặt trước Sách': reservations_page(user)
    elif page=='Tài khoản & Phân quyền': accounts_page(user)
    elif page=='Trợ lý AI & Gợi ý Sách': ai_recommend_page(user)
    elif page=='Báo cáo & Xuất dữ liệu': reports_page(user)
    elif page=='Cài đặt': settings_page(user)
else:
    if page=='Trang chủ Hội viên': reader_member_home(user)
    elif page=='Quản lý tài khoản': reader_account_page(user)
    elif page=='Tủ sách cá nhân': reader_shelf_page(user)
    elif page=='Quản lý đơn hàng': reader_orders_page(user)
    elif page=='Thành tích': reader_achievements_page(user)
    elif page=='Lịch sử giao dịch': reader_transactions_page(user)
    elif page=='Hỗ trợ khách hàng': reader_support_page(user)
    elif page=='Trợ lý AI & Gợi ý': reader_ai(user)
