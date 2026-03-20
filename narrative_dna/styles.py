APP_CSS = r"""
<style>
:root {
    --nd-blue: #123B7A;
    --nd-blue-hover: #0D2F63;
    --nd-soft-blue: #EEF4FF;
    --nd-text: #111827;
    --nd-muted: #5B6472;
    --nd-border: #DDE3EA;
    --nd-soft-border: #E8ECF1;
    --nd-card: #FFFFFF;
    --nd-page: #FFFFFF;
    --nd-sidebar: #F8FAFC;
    --nd-red: #B42318;
    --nd-amber: #A15C00;
    --nd-green: #166534;
}

html,
body,
[data-testid="stAppViewContainer"],
.stApp {
    background: var(--nd-page) !important;
    color: var(--nd-text) !important;
}

body,
button,
input,
textarea,
select {
    color: var(--nd-text);
}

.block-container {
    max-width: 1320px;
    padding-top: 1.35rem;
    padding-bottom: 4rem;
}

[data-testid="stHeader"] {
    background: rgba(255,255,255,.96);
}

[data-testid="stSidebar"] {
    background: var(--nd-sidebar) !important;
    border-right: 1px solid var(--nd-border);
}

[data-testid="stSidebar"] .block-container {
    padding-top: 1.3rem;
}

[data-testid="stSidebar"] * {
    color: var(--nd-text);
}

h1, h2, h3, h4, h5, h6,
p, label, div {
    color: inherit;
}

.nd-hero {
    padding: 1.55rem 1.7rem;
    border: 1px solid var(--nd-border);
    border-radius: 18px;
    background: var(--nd-card);
    margin-bottom: .48rem;
}

.nd-title {
    color: var(--nd-text);
    font-size: clamp(2.55rem, 5vw, 4.15rem);
    line-height: 1;
    font-weight: 850;
    letter-spacing: -.045em;
    margin: 0 0 .78rem 0;
}

.nd-subtitle {
    font-size: 1.04rem;
    line-height: 1.65;
    max-width: 1040px;
    color: var(--nd-muted);
    margin: 0;
}

.nd-creator-strip {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: .34rem .52rem;
    padding: .62rem .86rem;
    border: 1px solid var(--nd-border);
    border-left: 4px solid var(--nd-blue);
    border-radius: 12px;
    background: var(--nd-card);
    font-size: .82rem;
    line-height: 1.35;
    margin-bottom: .95rem;
}

.nd-creator-label {
    color: var(--nd-blue);
    font-size: .69rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: .08em;
}

.nd-creator-name {
    color: var(--nd-text);
    font-weight: 800;
}

.nd-creator-separator {
    color: #A0A8B3;
}

.nd-creator-meta {
    color: var(--nd-muted);
}

.nd-creator-email {
    color: var(--nd-blue) !important;
    text-decoration: none;
    font-weight: 600;
}

.nd-creator-email:hover {
    color: var(--nd-blue-hover) !important;
    text-decoration: underline;
}

.nd-section-title {
    color: var(--nd-text);
    font-size: clamp(1.55rem, 2.2vw, 1.78rem);
    line-height: 1.2;
    font-weight: 850;
    letter-spacing: -.025em;
    margin: 1.28rem 0 .82rem 0;
}

.nd-how-card {
    min-height: 118px;
    padding: .8rem .9rem .9rem;
    border: 1px solid var(--nd-border);
    border-radius: 14px;
    background: var(--nd-card);
    height: 100%;
}

.nd-how-head {
    display: flex;
    align-items: baseline;
    gap: .32rem;
    margin-bottom: .5rem;
}

.nd-step-number {
    color: var(--nd-blue);
    font-size: 1rem;
    line-height: 1.25;
    font-weight: 880;
    flex: 0 0 auto;
}

.nd-how-title {
    color: var(--nd-text);
    font-size: .96rem;
    line-height: 1.25;
    font-weight: 820;
}

.nd-how-text {
    font-size: .86rem;
    line-height: 1.48;
    color: var(--nd-muted);
}

.nd-score-card {
    padding: 1rem 1rem .94rem;
    border: 1px solid var(--nd-border);
    border-radius: 15px;
    background: var(--nd-card);
    min-height: 126px;
    height: 100%;
}

.nd-score-label {
    font-size: .73rem;
    font-weight: 820;
    letter-spacing: .065em;
    text-transform: uppercase;
    color: var(--nd-muted);
}

.nd-score-value {
    color: var(--nd-text);
    font-size: 2.18rem;
    line-height: 1.05;
    font-weight: 880;
    letter-spacing: -.04em;
    margin-top: .5rem;
}

.nd-score-note {
    font-size: .81rem;
    line-height: 1.4;
    color: var(--nd-muted);
    margin-top: .34rem;
}

.nd-assessment {
    border: 1px solid var(--nd-border);
    border-left: 5px solid var(--nd-blue);
    border-radius: 15px;
    background: var(--nd-card);
    padding: 1.08rem 1.2rem;
    margin: .95rem 0;
}

.nd-assessment-label {
    color: var(--nd-text);
    font-weight: 850;
    font-size: 1.08rem;
    margin-bottom: .38rem;
}

.nd-assessment-text {
    color: var(--nd-muted);
    line-height: 1.62;
}

.nd-mini-card {
    padding: .95rem 1rem;
    border: 1px solid var(--nd-border);
    border-radius: 14px;
    background: var(--nd-card);
    height: 100%;
}

.nd-mini-label {
    color: var(--nd-blue);
    text-transform: uppercase;
    letter-spacing: .065em;
    font-size: .69rem;
    font-weight: 820;
}

.nd-mini-value {
    color: var(--nd-text);
    margin-top: .36rem;
    font-weight: 720;
    line-height: 1.5;
}

.nd-warning {
    border: 1px solid var(--nd-border);
    border-left: 5px solid var(--nd-red);
    border-radius: 14px;
    padding: 1rem 1.05rem;
    margin-bottom: .72rem;
    background: var(--nd-card);
}

.nd-warning.moderate {
    border-left-color: var(--nd-amber);
}

.nd-warning.low {
    border-left-color: var(--nd-green);
}

.nd-warning-top {
    display: flex;
    justify-content: space-between;
    gap: .75rem;
    align-items: baseline;
}

.nd-warning-title {
    color: var(--nd-text);
    font-weight: 820;
}

.nd-warning-severity {
    font-size: .73rem;
    font-weight: 820;
    color: var(--nd-muted);
    text-transform: uppercase;
    letter-spacing: .05em;
    white-space: nowrap;
}

.nd-warning-text {
    color: var(--nd-muted);
    line-height: 1.55;
    margin-top: .38rem;
}

.nd-model-card {
    margin-top: .85rem;
    padding: .82rem .88rem;
    border: 1px solid #CAD8EC;
    border-radius: 13px;
    background: var(--nd-soft-blue);
    font-size: .83rem;
    line-height: 1.55;
}

.nd-model-card strong {
    color: var(--nd-blue);
}

/* Result navigation: deliberately prominent. */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    gap: .2rem;
    border-bottom: 1px solid var(--nd-border);
    margin-bottom: .95rem;
}

[data-testid="stTabs"] button[data-baseweb="tab"],
[data-testid="stTabs"] button[role="tab"] {
    min-height: 3.75rem;
    padding: .8rem 1.22rem;
    color: #263244 !important;
    border-radius: 9px 9px 0 0;
}

[data-testid="stTabs"] button[data-baseweb="tab"] p,
[data-testid="stTabs"] button[role="tab"] p {
    font-size: 1.14rem !important;
    line-height: 1.2 !important;
    font-weight: 760 !important;
    color: inherit !important;
}

[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"],
[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
    color: var(--nd-blue) !important;
    background: var(--nd-soft-blue) !important;
}

[data-testid="stTabs"] [data-baseweb="tab-highlight"] {
    background-color: var(--nd-blue) !important;
    height: 4px !important;
    border-radius: 4px 4px 0 0;
}

/* White, lightly framed analytical surfaces. */
[data-testid="stPlotlyChart"] {
    background: #FFFFFF;
    border: 1px solid var(--nd-border);
    border-radius: 15px;
    padding: .35rem;
    overflow: hidden;
}

[data-testid="stDataFrame"] {
    border: 1px solid var(--nd-border);
    border-radius: 13px;
    overflow: hidden;
    background: #FFFFFF;
}

[data-testid="stExpander"] {
    border-color: var(--nd-border) !important;
    border-radius: 12px !important;
    background: #FFFFFF !important;
}

hr {
    border-color: var(--nd-soft-border) !important;
}

div[data-testid="stTextArea"] textarea,
div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] > div > div {
    color: var(--nd-text) !important;
    background: #FFFFFF !important;
    border-color: var(--nd-border) !important;
    border-radius: 12px !important;
}

div[data-testid="stTextArea"] textarea {
    min-height: 250px;
}

.stButton > button,
.stDownloadButton > button {
    border-radius: 11px;
    font-weight: 760;
    min-height: 2.8rem;
}

.stButton > button[kind="primary"],
.stButton > button[data-testid="stBaseButton-primary"] {
    background: var(--nd-blue) !important;
    border-color: var(--nd-blue) !important;
    color: #FFFFFF !important;
}

.stButton > button[kind="primary"]:hover,
.stButton > button[data-testid="stBaseButton-primary"]:hover {
    background: var(--nd-blue-hover) !important;
    border-color: var(--nd-blue-hover) !important;
}

[data-testid="stMetric"] {
    border: 1px solid var(--nd-border);
    border-radius: 14px;
    padding: .8rem;
    background: #FFFFFF;
}

@media (max-width: 900px) {
    .nd-title {
        font-size: 2.7rem;
    }

    .nd-creator-strip {
        align-items: flex-start;
    }

    [data-testid="stTabs"] button[data-baseweb="tab"],
    [data-testid="stTabs"] button[role="tab"] {
        min-height: 3.35rem;
        padding: .7rem .7rem;
    }

    [data-testid="stTabs"] button[data-baseweb="tab"] p,
    [data-testid="stTabs"] button[role="tab"] p {
        font-size: .98rem !important;
    }
}
</style>
"""
