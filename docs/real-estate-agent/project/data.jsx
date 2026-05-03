// Real Estate Agent — shared data + primitives
// UAE-themed mock listings, agents, leads, etc.

const EMIRATES = ['Dubai', 'Abu Dhabi', 'Sharjah', 'Ajman', 'Ras Al Khaimah'];

const PROPERTIES = [
  { id:'P-1042', title:'Marina Penthouse · Bay View', area:'Dubai Marina', emirate:'Dubai',
    price:8_400_000, beds:3, baths:4, sqft:3210, type:'Penthouse', listed:'2 days ago',
    img:'img-1', lat:32, lng:38, agent:'Layla Al Rashid', match:96, trend:'+4.2%',
    features:['Sea view','Private pool','Smart home','Concierge'],
    desc:'A 32nd-floor penthouse on Marina Walk with panoramic views of the Gulf. Floor-to-ceiling glazing, an open kitchen by Boffi, and a 60 sqm wraparound terrace. Building amenities include a heated lap pool, padel court and 24/7 concierge.' },
  { id:'P-1038', title:'Saadiyat Beach Villa', area:'Saadiyat Island', emirate:'Abu Dhabi',
    price:14_200_000, beds:5, baths:6, sqft:6840, type:'Villa', listed:'5 days ago',
    img:'img-2', lat:60, lng:18, agent:'Omar Al Mansouri', match:92, trend:'+3.8%',
    features:['Beach access','Garden','Maid\'s room','Private gym'],
    desc:'A modern villa steps from Saadiyat Beach Club. Travertine and walnut interiors, a 12m lap pool, and a landscaped garden with mature olive trees. Walking distance to the Louvre Abu Dhabi.' },
  { id:'P-1036', title:'JBR Skyline Apartment', area:'JBR', emirate:'Dubai',
    price:3_650_000, beds:2, baths:3, sqft:1580, type:'Apartment', listed:'1 week ago',
    img:'img-3', lat:24, lng:52, agent:'Layla Al Rashid', match:88, trend:'+2.1%',
    features:['Beach access','Walkable','Shared pool'],
    desc:'A bright two-bedroom on the 24th floor of JBR\'s Bahar tower. Direct access to The Walk and the open beach.' },
  { id:'P-1031', title:'Al Reem Townhouse', area:'Al Reem Island', emirate:'Abu Dhabi',
    price:4_900_000, beds:4, baths:4, sqft:3120, type:'Townhouse', listed:'1 week ago',
    img:'img-4', lat:72, lng:62, agent:'Omar Al Mansouri', match:85, trend:'+1.4%',
    features:['Garden','Family-friendly','Pool'],
    desc:'A four-bedroom townhouse in a gated community with shared pool, gym and kids\' play area.' },
  { id:'P-1027', title:'Al Khan Lagoon Villa', area:'Al Khan', emirate:'Sharjah',
    price:2_800_000, beds:5, baths:5, sqft:4200, type:'Villa', listed:'2 weeks ago',
    img:'img-5', lat:50, lng:75, agent:'Fatima Hosani', match:81, trend:'+0.8%',
    features:['Lagoon view','Garage 3','Mature garden'],
    desc:'A five-bedroom villa on a quiet cul-de-sac with direct lagoon frontage and a private dock.' },
  { id:'P-1024', title:'Al Hamra Marina Loft', area:'Al Hamra Village', emirate:'Ras Al Khaimah',
    price:1_650_000, beds:2, baths:2, sqft:1340, type:'Apartment', listed:'2 weeks ago',
    img:'img-6', lat:38, lng:80, agent:'Hassan Karimi', match:79, trend:'+1.9%',
    features:['Marina view','Resort facilities','Golf course'],
    desc:'A two-bedroom loft in the Al Hamra resort cluster overlooking the marina, with access to the championship golf course.' },
  { id:'P-1019', title:'Ajman Corniche Apartment', area:'Ajman Corniche', emirate:'Ajman',
    price:920_000, beds:2, baths:2, sqft:1180, type:'Apartment', listed:'3 weeks ago',
    img:'img-7', lat:84, lng:34, agent:'Hassan Karimi', match:74, trend:'+0.4%',
    features:['Sea view','Balcony'],
    desc:'A two-bedroom corner unit on the Ajman corniche with a 14m balcony.' },
  { id:'P-1015', title:'Downtown Burj View', area:'Downtown Dubai', emirate:'Dubai',
    price:6_100_000, beds:3, baths:3, sqft:2240, type:'Apartment', listed:'3 weeks ago',
    img:'img-8', lat:18, lng:28, agent:'Layla Al Rashid', match:90, trend:'+5.1%',
    features:['Burj view','Walkable','Smart home'],
    desc:'A three-bedroom on the 47th floor with an unobstructed view of the Burj Khalifa fountain show.' },
];

const AGENTS = [
  { id:'a1', name:'Layla Al Rashid', initials:'LR', color:'',
    role:'Senior Advisor · Dubai', listings:18, deals:7, rating:4.9 },
  { id:'a2', name:'Omar Al Mansouri', initials:'OM', color:'purple',
    role:'Senior Advisor · Abu Dhabi', listings:14, deals:5, rating:4.8 },
  { id:'a3', name:'Fatima Hosani', initials:'FH', color:'amber',
    role:'Advisor · Sharjah', listings:9, deals:3, rating:4.7 },
  { id:'a4', name:'Hassan Karimi', initials:'HK', color:'rose',
    role:'Advisor · Northern Emirates', listings:11, deals:4, rating:4.8 },
];

const LEADS = [
  { id:'L-308', name:'Reem Al Suwaidi', stage:'new', source:'Website', budget:'AED 4-6M',
    interest:'Marina, JBR · 2-3BR', updated:'12 min ago', heat:'hot', match:94, avatar:'RA', color:'' },
  { id:'L-307', name:'James Patterson', stage:'new', source:'Referral', budget:'AED 8-12M',
    interest:'Saadiyat villa · 4BR+', updated:'34 min ago', heat:'hot', match:91, avatar:'JP', color:'purple' },
  { id:'L-301', name:'Aisha Bin Suroor', stage:'qualified', source:'Property Finder', budget:'AED 2-3M',
    interest:'Sharjah lagoon · family', updated:'2h ago', heat:'warm', match:82, avatar:'AB', color:'amber' },
  { id:'L-296', name:'David Chen', stage:'qualified', source:'Bayut', budget:'AED 1.5-2M',
    interest:'RAK Al Hamra · investment', updated:'4h ago', heat:'warm', match:78, avatar:'DC', color:'rose' },
  { id:'L-291', name:'Mariam Tanveer', stage:'viewing', source:'Instagram', budget:'AED 3-4M',
    interest:'JBR 2BR · sea view', updated:'yesterday', heat:'warm', match:85, avatar:'MT', color:'purple' },
  { id:'L-285', name:'Carlos Mendez', stage:'viewing', source:'Website', budget:'AED 6-8M',
    interest:'Downtown 3BR', updated:'yesterday', heat:'hot', match:89, avatar:'CM', color:'amber' },
  { id:'L-279', name:'Yasmin Al Habsi', stage:'offer', source:'Referral', budget:'AED 14M',
    interest:'Saadiyat 5BR villa', updated:'2 days ago', heat:'hot', match:96, avatar:'YH', color:'' },
  { id:'L-272', name:'Tomás Rivera', stage:'closed', source:'Bayut', budget:'AED 6.1M',
    interest:'Downtown Burj View', updated:'closed last wk', heat:'cold', match:100, avatar:'TR', color:'rose' },
];

const STAGES = [
  { key:'new',       label:'New',           accent:'#22d3ee' },
  { key:'qualified', label:'Qualified',     accent:'#a78bfa' },
  { key:'viewing',   label:'Viewing',       accent:'#fbbf24' },
  { key:'offer',     label:'Offer',         accent:'#f97316' },
  { key:'closed',    label:'Closed Won',    accent:'#4ade80' },
];

const DOCUMENTS = [
  { id:'D-104', name:'SPA · Yasmin Al Habsi', kind:'Sale Agreement', status:'awaiting-signatures',
    property:'P-1038', value:14_200_000, updated:'2h ago', progress:75 },
  { id:'D-103', name:'NOC Application · Tomás R.', kind:'NOC',  status:'submitted',
    property:'P-1015', value:6_100_000, updated:'yesterday', progress:100 },
  { id:'D-101', name:'MoU · Carlos Mendez', kind:'MoU', status:'drafting',
    property:'P-1015', value:6_100_000, updated:'3h ago', progress:35 },
  { id:'D-099', name:'Mortgage Pre-Approval · D. Chen', kind:'Mortgage', status:'awaiting-bank',
    property:'P-1024', value:1_650_000, updated:'1d ago', progress:60 },
  { id:'D-097', name:'Disclosure pack · Reem A.', kind:'Disclosure', status:'auto-generated',
    property:'P-1042', value:8_400_000, updated:'10 min ago', progress:90 },
];

const AUTOMATIONS = [
  { id:'auto-1', name:'New-lead qualifier', desc:'Scores incoming leads, asks 4 questions, books a viewing if hot.',
    runs:412, success:96, status:'running', icon:'inbox' },
  { id:'auto-2', name:'Listing market analysis', desc:'Pulls comparables, writes a market report when a listing goes live.',
    runs:184, success:99, status:'running', icon:'bar-chart' },
  { id:'auto-3', name:'Viewing follow-up', desc:'24h after a viewing, sends a tailored note + 3 similar listings.',
    runs:98, success:88, status:'running', icon:'send' },
  { id:'auto-4', name:'Document auto-draft', desc:'Generates MoU, NOC and disclosure packs from listing + lead data.',
    runs:46, success:100, status:'running', icon:'file' },
  { id:'auto-5', name:'Price-drop alerts', desc:'Notifies matched leads when any saved listing drops 3%+.',
    runs:312, success:100, status:'paused', icon:'bell' },
];

const APPOINTMENTS = [
  { time:'09:30', date:'Today', title:'Viewing · Marina Penthouse', who:'Reem Al Suwaidi', kind:'viewing' },
  { time:'11:00', date:'Today', title:'Call · pre-approval', who:'David Chen', kind:'call' },
  { time:'14:00', date:'Today', title:'Viewing · Downtown Burj View', who:'Carlos Mendez', kind:'viewing' },
  { time:'16:30', date:'Today', title:'Offer review', who:'Yasmin Al Habsi', kind:'offer' },
  { time:'10:00', date:'Tomorrow', title:'Viewing · Saadiyat villa', who:'James Patterson', kind:'viewing' },
  { time:'15:00', date:'Tomorrow', title:'Closing · Tomás Rivera', who:'Tomás Rivera', kind:'closing' },
];

const fmtAED = n => {
  if (n >= 1_000_000) return `AED ${(n/1_000_000).toFixed(2).replace(/\.?0+$/,'')}M`;
  if (n >= 1_000) return `AED ${(n/1000).toFixed(0)}K`;
  return `AED ${n}`;
};
const fmtAEDShort = n => `AED ${(n/1_000_000).toFixed(1)}M`;

// Architectural decoration SVG for property image placeholders
const ArchLines = ({ variant=1 }) => {
  const variants = {
    1: ( // tower silhouette
      <>
        <rect x="20" y="40" width="22" height="160" stroke="rgba(255,255,255,0.18)" strokeWidth="0.5" fill="none"/>
        <rect x="50" y="20" width="28" height="180" stroke="rgba(255,255,255,0.22)" strokeWidth="0.5" fill="none"/>
        <rect x="86" y="60" width="22" height="140" stroke="rgba(255,255,255,0.16)" strokeWidth="0.5" fill="none"/>
        <rect x="116" y="35" width="24" height="165" stroke="rgba(255,255,255,0.18)" strokeWidth="0.5" fill="none"/>
        <rect x="148" y="55" width="22" height="145" stroke="rgba(255,255,255,0.14)" strokeWidth="0.5" fill="none"/>
        {[...Array(20)].map((_,i)=>(
          <line key={i} x1="0" y1={50+i*8} x2="200" y2={50+i*8}
            stroke="rgba(255,255,255,0.04)" strokeWidth="0.5"/>
        ))}
        <line x1="0" y1="200" x2="200" y2="200" stroke="rgba(34,211,238,0.4)" strokeWidth="0.5"/>
      </>
    ),
    2: ( // villa silhouette
      <>
        <rect x="30" y="100" width="140" height="80" stroke="rgba(255,255,255,0.20)" strokeWidth="0.5" fill="none"/>
        <line x1="30" y1="130" x2="170" y2="130" stroke="rgba(255,255,255,0.12)" strokeWidth="0.5"/>
        <rect x="50" y="115" width="20" height="14" stroke="rgba(255,255,255,0.22)" strokeWidth="0.5" fill="none"/>
        <rect x="80" y="115" width="20" height="14" stroke="rgba(255,255,255,0.22)" strokeWidth="0.5" fill="none"/>
        <rect x="110" y="115" width="20" height="14" stroke="rgba(255,255,255,0.22)" strokeWidth="0.5" fill="none"/>
        <rect x="140" y="115" width="20" height="14" stroke="rgba(255,255,255,0.22)" strokeWidth="0.5" fill="none"/>
        <line x1="0" y1="180" x2="200" y2="180" stroke="rgba(34,211,238,0.4)" strokeWidth="0.5"/>
      </>
    ),
    3: ( // grid horizon
      <>
        {[...Array(10)].map((_,i)=>(
          <line key={i} x1={20+i*18} y1="60" x2={20+i*18} y2="180" stroke="rgba(255,255,255,0.08)" strokeWidth="0.5"/>
        ))}
        {[...Array(8)].map((_,i)=>(
          <line key={i} x1="20" y1={60+i*15} x2="200" y2={60+i*15} stroke="rgba(255,255,255,0.08)" strokeWidth="0.5"/>
        ))}
        <line x1="0" y1="180" x2="200" y2="180" stroke="rgba(34,211,238,0.4)" strokeWidth="0.5"/>
      </>
    ),
  };
  return (
    <svg className="archlines" viewBox="0 0 200 220" preserveAspectRatio="none">
      {variants[((variant-1) % 3) + 1]}
    </svg>
  );
};

// Lucide-style stroke icons (24x24)
const Icon = ({ name, size=20, stroke=1.75 }) => {
  const paths = {
    home: <><path d="M3 12L12 3l9 9"/><path d="M5 10v10h14V10"/></>,
    search: <><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></>,
    map: <><path d="M9 3 3 6v15l6-3 6 3 6-3V3l-6 3-6-3z"/><path d="M9 3v15"/><path d="M15 6v15"/></>,
    sparkles: <><path d="M12 3v4M12 17v4M3 12h4M17 12h4"/><path d="m6 6 2 2M16 16l2 2M6 18l2-2M16 8l2-2"/></>,
    chat: <><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></>,
    users: <><circle cx="9" cy="8" r="4"/><path d="M2 21v-2a4 4 0 0 1 4-4h6a4 4 0 0 1 4 4v2"/><circle cx="17" cy="8" r="3"/><path d="M22 21v-1a3 3 0 0 0-3-3"/></>,
    chart: <><path d="M3 3v18h18"/><path d="m7 14 4-4 4 4 5-5"/></>,
    file: <><path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"/><path d="M14 3v6h6"/></>,
    cog: <><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 1 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.6 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 1 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.6a1.65 1.65 0 0 0 1-1.51V3a2 2 0 1 1 4 0v.09A1.65 1.65 0 0 0 15 4.6a1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 1 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></>,
    cal: <><rect x="3" y="4" width="18" height="18" rx="2"/><path d="M16 2v4M8 2v4M3 10h18"/></>,
    bed: <><path d="M3 18V8h13a4 4 0 0 1 4 4v6"/><path d="M3 14h18"/><circle cx="7" cy="11" r="2"/></>,
    bath: <><path d="M4 12V5a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v1"/><path d="M3 12h18v3a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4v-3z"/><path d="M7 19l-1 2M17 19l1 2"/></>,
    sqft: <><rect x="3" y="3" width="18" height="18"/><path d="M9 3v18M3 9h18"/></>,
    pin: <><path d="M12 22s8-7 8-13a8 8 0 0 0-16 0c0 6 8 13 8 13z"/><circle cx="12" cy="9" r="3"/></>,
    heart: <><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></>,
    share: <><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="m8.6 13.5 6.8 4M15.4 6.5l-6.8 4"/></>,
    plus: <><path d="M12 5v14M5 12h14"/></>,
    chevR: <><path d="m9 18 6-6-6-6"/></>,
    chevL: <><path d="m15 18-6-6 6-6"/></>,
    chevD: <><path d="m6 9 6 6 6-6"/></>,
    x: <><path d="M18 6 6 18M6 6l18 18" transform="scale(0.66)"/></>,
    send: <><path d="m22 2-7 20-4-9-9-4z"/><path d="m22 2-11 11"/></>,
    bell: <><path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></>,
    play: <><polygon points="5 3 19 12 5 21 5 3"/></>,
    pause: <><rect x="6" y="4" width="4" height="16"/><rect x="14" y="4" width="4" height="16"/></>,
    inbox: <><path d="M22 12h-6l-2 3h-4l-2-3H2"/><path d="M5.45 5.11 2 12v6a2 2 0 0 0 2 2h16a2 2 0 0 0 2-2v-6l-3.45-6.89A2 2 0 0 0 16.76 4H7.24a2 2 0 0 0-1.79 1.11z"/></>,
    'bar-chart': <><path d="M12 20V10M18 20V4M6 20v-4"/></>,
    star: <><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></>,
    flame: <><path d="M8.5 14.5A2.5 2.5 0 0 0 11 12c0-1.38-.5-2-1-3-1.072-2.143-.224-4.054 2-6 .5 2.5 2 4.9 4 6.5 2 1.6 3 3.5 3 5.5a7 7 0 1 1-14 0c0-1.153.433-2.294 1-3a2.5 2.5 0 0 0 2.5 2.5z"/></>,
    filter: <><polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/></>,
    grid: <><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></>,
    list: <><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><circle cx="4" cy="6" r="0.5"/><circle cx="4" cy="12" r="0.5"/><circle cx="4" cy="18" r="0.5"/></>,
    download: <><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></>,
    edit: <><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></>,
    check: <><polyline points="20 6 9 17 4 12"/></>,
    sun: <><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4 12H2M22 12h-2M5.6 5.6 4.2 4.2M19.8 19.8l-1.4-1.4M5.6 18.4 4.2 19.8M19.8 4.2l-1.4 1.4"/></>,
    eye: <><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7z"/><circle cx="12" cy="12" r="3"/></>,
    pen: <><path d="M12 19l7-7 3 3-7 7-3-3z"/><path d="M18 13l-1.5-7.5L2 2l3.5 14.5L13 18l5-5z"/><path d="M2 2l7.586 7.586"/></>,
    clock: <><circle cx="12" cy="12" r="9"/><path d="M12 7v5l4 2"/></>,
    phone: <><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"/></>,
    handshake: <><path d="M11 17l2 2 4-4"/><path d="M3 8l4-4 4 3 4-3 4 4-7 9-2-1-3-3z"/></>,
  };
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="none"
      stroke="currentColor" strokeWidth={stroke}
      strokeLinecap="round" strokeLinejoin="round" style={{flexShrink:0}}>
      {paths[name]||null}
    </svg>
  );
};

// ============ BUYER-FACING DATA ============
// The user's own offers, alerts, viewings, and saved-search activity

const MY_OFFERS = [
  { id:'O-204', propertyId:'P-1042', stage:'countered',
    listPrice:8_400_000, myOffer:7_950_000, counter:8_200_000,
    submitted:'2 days ago', updated:'5h ago',
    note:'Seller wants 8.2M. AI suggests 8.05M as walk-up — they\'ve had 4 lower offers refused.' },
  { id:'O-198', propertyId:'P-1015', stage:'submitted',
    listPrice:6_100_000, myOffer:5_900_000,
    submitted:'yesterday', updated:'1h ago',
    note:'Submitted via Sceptre. Seller has 72 hours to respond per UAE protocol.' },
  { id:'O-192', propertyId:'P-1024', stage:'drafting',
    listPrice:1_650_000, myOffer:1_580_000,
    submitted:'just now', updated:'just now',
    note:'Draft offer — review the AI valuation before submitting.' },
  { id:'O-187', propertyId:'P-1036', stage:'accepted',
    listPrice:3_650_000, myOffer:3_500_000,
    submitted:'4 days ago', updated:'this morning',
    note:'Accepted. NOC and SPA are auto-drafted in My Documents.' },
  { id:'O-179', propertyId:'P-1019', stage:'rejected',
    listPrice:920_000, myOffer:830_000,
    submitted:'1 week ago', updated:'3 days ago',
    note:'Seller declined. AI flagged 2 similar units within 8% of your target.' },
];

const OFFER_STAGES = [
  { key:'drafting',  label:'Drafting',     accent:'#94a3b8' },
  { key:'submitted', label:'Submitted',    accent:'#22d3ee' },
  { key:'countered', label:'Countered',    accent:'#fbbf24' },
  { key:'accepted',  label:'Accepted',     accent:'#4ade80' },
  { key:'rejected',  label:'Closed',       accent:'#64748b' },
];

const MY_ALERTS = [
  { id:'al-1', name:'Price drops on saved homes', desc:'Notify me when any saved listing drops 3% or more.',
    runs:8, lastFire:'2 days ago — P-1027 dropped 3.5%', status:'on', icon:'bell' },
  { id:'al-2', name:'New matches for "Marina sea-view 3BR"', desc:'Surface listings under AED 9M matching this saved search the moment they go live.',
    runs:14, lastFire:'this morning — 2 new', status:'on', icon:'sparkles' },
  { id:'al-3', name:'Comparable sales nearby', desc:'Weekly digest of closed sales in areas you\'re shortlisting.',
    runs:6, lastFire:'Sunday — 11 sales in your areas', status:'on', icon:'bar-chart' },
  { id:'al-4', name:'Mortgage rate watch', desc:'Track ENBD, Mashreq, FAB rates and ping me when they move 0.25%+.',
    runs:31, lastFire:'yesterday — ENBD -0.15%', status:'on', icon:'chart' },
  { id:'al-5', name:'Viewing reminders', desc:'24h, 2h and 30min before each scheduled viewing.',
    runs:12, lastFire:'tomorrow 09:00 (Marina Penthouse)', status:'on', icon:'cal' },
  { id:'al-6', name:'Offer status updates', desc:'Push notifications when sellers respond to your offers.',
    runs:5, lastFire:'5h ago — counter on P-1042', status:'on', icon:'inbox' },
  { id:'al-7', name:'Open-house digests', desc:'Daily summary of open houses in your saved areas.',
    runs:0, lastFire:'never — paused', status:'off', icon:'eye' },
];

const MY_DOCUMENTS = [
  { id:'D-201', name:'Sale Agreement · Marina Penthouse', kind:'SPA',
    status:'awaiting-you', property:'P-1042', value:8_400_000,
    updated:'5h ago', progress:60, action:'2 signatures from you' },
  { id:'D-200', name:'Mortgage Pre-Approval · ENBD', kind:'Mortgage',
    status:'awaiting-bank', property:'P-1042', value:8_400_000,
    updated:'yesterday', progress:75, action:'Bank reviewing' },
  { id:'D-198', name:'NOC · Downtown Burj View', kind:'NOC',
    status:'submitted', property:'P-1015', value:6_100_000,
    updated:'2 days ago', progress:100, action:null },
  { id:'D-194', name:'MoU · JBR Skyline', kind:'MoU',
    status:'completed', property:'P-1036', value:3_650_000,
    updated:'last week', progress:100, action:null },
  { id:'D-188', name:'Title check · Saadiyat villa', kind:'Due diligence',
    status:'auto-generated', property:'P-1038', value:14_200_000,
    updated:'15 min ago', progress:90, action:'Review AI summary' },
  { id:'D-182', name:'Disclosure pack · Reem A.', kind:'Disclosure',
    status:'auto-generated', property:'P-1024', value:1_650_000,
    updated:'1h ago', progress:85, action:'Review AI summary' },
];

const MY_VIEWINGS = [
  { time:'Tomorrow · 09:00', title:'Marina Penthouse · Bay View', who:'with Layla Al Rashid',
    address:'Marina Walk, Tower 6 · 32nd floor', kind:'viewing', propertyId:'P-1042' },
  { time:'Tomorrow · 11:30', title:'ENBD pre-approval call', who:'Salem Al Marri (Mortgage advisor)',
    address:'Video call — Sceptre will dial you in', kind:'call', propertyId:null },
  { time:'Wed · 14:00', title:'Downtown Burj View walkthrough', who:'with Layla Al Rashid',
    address:'Burj Vista, T1 · 47th floor', kind:'viewing', propertyId:'P-1015' },
  { time:'Thu · 16:30', title:'Offer review on Saadiyat villa', who:'with Sceptre AI + Layla',
    address:'Video call · 30 min', kind:'offer', propertyId:'P-1038' },
  { time:'Fri · 11:00', title:'Saadiyat Beach Villa', who:'with Omar Al Mansouri',
    address:'Saadiyat Beach Residences · Plot 14', kind:'viewing', propertyId:'P-1038' },
];

const MY_ACTIVITY = [
  { t:'09:42', who:'Sceptre', kind:'alert',  msg:'Price drop on P-1027 (-3.5%) · matches your "Sharjah lagoon" search' },
  { t:'08:30', who:'Layla',   kind:'human',  msg:'Confirmed your viewing tomorrow 9am · I\'ll meet you in the lobby' },
  { t:'Yest',  who:'Seller',  kind:'offer',  msg:'Counter-offer on Marina Penthouse: AED 8.2M (you offered 7.95M)' },
  { t:'Yest',  who:'Sceptre', kind:'doc',    msg:'Auto-drafted SPA for P-1042 · ready for your signatures' },
  { t:'Yest',  who:'Sceptre', kind:'match',  msg:'2 new listings matched "Marina sea-view 3BR" · 96% and 91% match' },
  { t:'2d ago',who:'ENBD',    kind:'mortgage',msg:'Pre-approval received · AED 6.3M @ 4.42% fixed 25y' },
  { t:'2d ago',who:'Sceptre', kind:'alert',  msg:'Saadiyat 5BR comp set up 3.8% MoM · now\'s a good moment to submit' },
  { t:'3d ago',who:'You',     kind:'self',   msg:'Saved JBR Skyline Apartment to wishlist' },
];

Object.assign(window, {
  EMIRATES, PROPERTIES, AGENTS, LEADS, STAGES, DOCUMENTS, AUTOMATIONS, APPOINTMENTS,
  MY_OFFERS, OFFER_STAGES, MY_ALERTS, MY_DOCUMENTS, MY_VIEWINGS, MY_ACTIVITY,
  fmtAED, fmtAEDShort, ArchLines, Icon,
});
