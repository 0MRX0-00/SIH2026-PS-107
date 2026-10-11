/**
 * Laboratory Multilingual Localization & Transliteration Engine
 * Translates and transliterates Indian laboratory names, cities, states,
 * and recognition schemes into natural, authentic Hindi (हिन्दी) and Tamil (தமிழ்).
 */

export const CITY_LOCALIZATION: Record<string, { hi: string; ta: string }> = {
  ahmedabad: { hi: "अहमदाबाद", ta: "அகமதாபாத்" },
  bangalore: { hi: "बेंगलुरु", ta: "பெங்களூரு" },
  bengaluru: { hi: "बेंगलुरु", ta: "பெங்களூரு" },
  chennai: { hi: "चेन्नई", ta: "சென்னை" },
  madras: { hi: "चेन्नई", ta: "சென்னை" },
  mumbai: { hi: "मुंबई", ta: "மும்பை" },
  bombay: { hi: "मुंबई", ta: "மும்பை" },
  delhi: { hi: "दिल्ली", ta: "டெல்லி" },
  "new delhi": { hi: "नई दिल्ली", ta: "புது டெல்லி" },
  kolkata: { hi: "कोलकाता", ta: "கொல்கத்தா" },
  calcutta: { hi: "कोलकाता", ta: "கொல்கத்தா" },
  hyderabad: { hi: "हैदराबाद", ta: "ஹைதராபாத்" },
  pune: { hi: "पुणे", ta: "புனே" },
  vadodara: { hi: "वडोदरा", ta: "வதோதரா" },
  baroda: { hi: "वडोदरा", ta: "வதோதரா" },
  ghaziabad: { hi: "गाजियाबाद", ta: "காசியாபாத்" },
  sahibabad: { hi: "साहिबाबाद", ta: "சாஹிபாபாத்" },
  gurgaon: { hi: "गुरुग्राम", ta: "குருகிராம்" },
  gurugram: { hi: "गुरुग्राम", ta: "குருகிராம்" },
  noida: { hi: "नोएडा", ta: "நொய்டா" },
  "greater noida": { hi: "ग्रेटर नोएडा", ta: "கிரேட்டர் நொய்டா" },
  faridabad: { hi: "फरीदाबाद", ta: "பரிதாபாத்" },
  jaipur: { hi: "जयपुर", ta: "ஜெய்ப்பூர்" },
  coimbatore: { hi: "कोयंबटूर", ta: "கோயம்புத்தூர்" },
  kanpur: { hi: "कानपुर", ta: "கான்பூர்" },
  lucknow: { hi: "लखनऊ", ta: "லக்னோ" },
  nagpur: { hi: "नागपुर", ta: "நாக்பூர்" },
  indore: { hi: "इंदौर", ta: "இந்தூர்" },
  bhopal: { hi: "भोपाल", ta: "போபால்" },
  surat: { hi: "सूरत", ta: "சூரத்" },
  rajkot: { hi: "राजकोट", ta: "ராஜ்கோட்" },
  thiruvananthapuram: { hi: "तिरुवनंतपुरम", ta: "திருவனந்தபுரம்" },
  trivandrum: { hi: "तिरुवनंतपुरम", ta: "திருவனந்தபுரம்" },
  kochi: { hi: "कोच्चि", ta: "கொச்சி" },
  cochin: { hi: "कोच्चि", ta: "கொச்சி" },
  visakhapatnam: { hi: "विशाखापत्तनम", ta: "விசாகப்பட்டினம்" },
  vizag: { hi: "विशाखापत्तनम", ta: "விசாகப்பட்டினம்" },
  patna: { hi: "पटना", ta: "பாட்னா" },
  bhubaneswar: { hi: "भुवनेश्वर", ta: "புவனேஸ்வர்" },
  guwahati: { hi: "गुवाहाटी", ta: "குவாஹாட்டி" },
  chandigarh: { hi: "चंडीगढ़", ta: "சண்டிகர்" },
  ludhiana: { hi: "लुधियाना", ta: "லூதியானா" },
  jalandhar: { hi: "जालंधर", ta: "ஜலந்தர்" },
  mohali: { hi: "मोहाली", ta: "மொஹாலி" },
  mysore: { hi: "मैसूर", ta: "மைசூர்" },
  mysuru: { hi: "मैसूर", ta: "மைசூர்" },
  madurai: { hi: "मदुरै", ta: "மதுரை" },
  tirupur: { hi: "तिरुपुर", ta: "திருப்பூர்" },
  salem: { hi: "सलेम", ta: "சேலம்" },
  hosur: { hi: "होसुर", ta: "ஓசூர்" },
  ranipet: { hi: "रानीपेट", ta: "ராணிப்பேட்டை" },
  haridwar: { hi: "हरिद्वार", ta: "ஹரித்வார்" },
  dehradun: { hi: "देहरादून", ta: "டேஹ்ராடூன்" },
  roorkee: { hi: "रुड़की", ta: "ரூர்க்கி" },
  jamshedpur: { hi: "जमशेदपुर", ta: "ஜம்ஷெட்பூர்" },
  ranchi: { hi: "राँची", ta: "ராஞ்சி" },
  raipur: { hi: "रायपुर", ta: "ராய்ப்பூர்" },
  agra: { hi: "आगरा", ta: "ஆக்ரா" },
  meerut: { hi: "मेरठ", ta: "மீரட்" },
  varanasi: { hi: "वाराणसी", ta: "வாரணாசி" },
  sonipat: { hi: "सोनीपत", ta: "சோனிபட்" },
  sonepat: { hi: "सोनीपत", ta: "சோனிபட்" },
  panipat: { hi: "पानीपत", ta: "பானிபட்" },
  kundli: { hi: "कुंडली", ta: "குண்ட்லி" },
  manesar: { hi: "मानेसर", ta: "மனேசர்" },
  bawana: { hi: "बवाना", ta: "பவானா" },
  okhla: { hi: "ओखला", ta: "ஓக்லா" },
  secunderabad: { hi: "सिकंदराबाद", ta: "செகந்திராபாத்" },
  vijayawada: { hi: "विजयवाड़ा", ta: "விஜயவாடா" },
  guntur: { hi: "गुंटूर", ta: "குண்டூர்" },
  nashik: { hi: "नासिक", ta: "நாசிக்" },
  aurangabad: { hi: "छत्रपति संभाजीनगर (औरंगाबाद)", ta: "அவுரங்காபாத்" },
  "chhatrapati sambhajinagar": { hi: "छत्रपति संभाजीनगर", ta: "சத்ரபதி சம்பாஜிநகர்" },
  tiruchirappalli: { hi: "तिरुचिरापल्ली", ta: "திருச்சிராப்பள்ளி" },
  trichy: { hi: "तिरुचिरापल्ली", ta: "திருச்சிராப்பள்ளி" },
  bathinda: { hi: "बठिंडा", ta: "பட்டிண்டா" },
  khargone: { hi: "खरगोन", ta: "கார்கோன்" },
  "cotton green": { hi: "कॉटन ग्रीन", ta: "காட்டன் கிரீன்" },
  anand: { hi: "आनंद", ta: "ஆனந்த்" },
  ambala: { hi: "अंबाला", ta: "அம்பாலா" },
  "ambala cantt": { hi: "अंबाला छावनी", ta: "அம்பாலா கண்டோன்மென்ட்" },
  baddi: { hi: "बद्दी", ta: "பட்டி" },
  bahadurgarh: { hi: "बहादुरगढ़", ta: "பகதூர்கர்" },
  durgapur: { hi: "दुर्गापुर", ta: "துர்காபூர்" },
  ernakulam: { hi: "एर्नाकुलम", ta: "எர்ணாகுளம்" },
  thane: { hi: "ठाणे", ta: "தானே" },
  "navi mumbai": { hi: "नवी मुंबई", ta: "நவி மும்பை" },
  panvel: { hi: "पनवेल", ta: "பன்வெல்" },
  morbi: { hi: "मोरबी", ta: "மோர்பி" },
  jamnagar: { hi: "जामनगर", ta: "ஜாம்நகர்" },
  parwanoo: { hi: "परवाणू", ta: "பர்வானூ" },
  derabassi: { hi: "डेराबस्सी", ta: "தேராபஸ்ஸி" },
  azadpur: { hi: "आजादपुर", ta: "ஆசாத்பூர்" },
  bahadrabad: { hi: "बहादराबाद", ta: "பகத்ராபாத்" },
  alappuzha: { hi: "अलप्पुझा", ta: "ஆலப்புழா" },
  vellore: { hi: "वेल्लोर", ta: "வேலூர்" },
  tirunelveli: { hi: "तिरुनेलवेली", ta: "திருநெல்வேலி" },
  palakkad: { hi: "पालक्काड़", ta: "பாலக்காடு" },
  kollam: { hi: "कोल्लम", ta: "கொல்லம்" },
  thrissur: { hi: "त्रिशूर", ta: "திருச்சூர்" },
  kannur: { hi: "कन्नूर", ta: "கண்ணூர்" },
  kozhikode: { hi: "कोझिकोड", ta: "கோழிக்கோடு" },
  calicut: { hi: "कोझिकोड", ta: "கோழிக்கோடு" },
};

export const STATE_LOCALIZATION: Record<string, { hi: string; ta: string }> = {
  delhi: { hi: "दिल्ली", ta: "டெல்லி" },
  maharashtra: { hi: "महाराष्ट्र", ta: "மகாராஷ்டிரா" },
  "tamil nadu": { hi: "तमिलनाडु", ta: "தமிழ்நாடு" },
  "uttar pradesh": { hi: "उत्तर प्रदेश", ta: "உத்தரப் பிரதேசம்" },
  "west bengal": { hi: "पश्चिम बंगाल", ta: "மேற்கு வங்காளம்" },
  karnataka: { hi: "कर्नाटक", ta: "கர்நாடகா" },
  gujarat: { hi: "गुजरात", ta: "குஜராத்" },
  rajasthan: { hi: "राजस्थान", ta: "ராஜஸ்தான்" },
  punjab: { hi: "पंजाब", ta: "பஞ்சாப்" },
  haryana: { hi: "हरियाणा", ta: "ஹரியானா" },
  kerala: { hi: "केरल", ta: "கேரளா" },
  "madhya pradesh": { hi: "मध्य प्रदेश", ta: "மத்தியப் பிரதேசம்" },
  telangana: { hi: "तेलंगाना", ta: "தெலுங்கானா" },
  "andhra pradesh": { hi: "आंध्र प्रदेश", ta: "ஆந்திரப் பிரதேசம்" },
  odisha: { hi: "ओडिशा", ta: "ஒடிசா" },
  bihar: { hi: "बिहार", ta: "பீகார்" },
  assam: { hi: "असम", ta: "அஸ்ஸாம்" },
  chhattisgarh: { hi: "छत्तीसगढ़", ta: "சத்தீஸ்கர்" },
  jharkhand: { hi: "झारखंड", ta: "ஜார்க்கண்ட்" },
  uttarakhand: { hi: "उत्तराखंड", ta: "உத்தரகாண்ட்" },
  "himachal pradesh": { hi: "हिमाचल प्रदेश", ta: "இமாச்சலப் பிரதேசம்" },
  "jammu & kashmir": { hi: "जम्मू और कश्मीर", ta: "ஜம்மு மற்றும் காஷ்மீர்" },
  goa: { hi: "गोवा", ta: "கோவா" },
  puducherry: { hi: "पुडुचेरी", ta: "புதுச்சேரி" },
  chandigarh: { hi: "चंडीगढ़", ta: "சண்டிகர்" },
};

// Institutional and common laboratory phrases sorted by length descending
const PHRASE_DICTIONARY: Array<{
  en: RegExp;
  hi: string;
  ta: string;
}> = [
  // Status prefixes
  { en: /\(deferred\)/gi, hi: "(आस्थगित)", ta: "(ஒத்திவைக்கப்பட்டது)" },

  // Key National & Statutory Institutions
  { en: /COTTON ASSOCIATION OF INDIA/gi, hi: "कॉटन एसोसिएशन ऑफ इंडिया", ta: "காட்டன் அசோசியேஷன் ஆஃப் இந்தியா" },
  { en: /COTTON TESTING AND RESEARCH LABORATORY/gi, hi: "कपास परीक्षण एवं अनुसंधान प्रयोगशाला", ta: "பருத்தி சோதனை மற்றும் ஆராய்ச்சி ஆய்வகம்" },
  { en: /COTTON TESTING & RESEARCH LABORATORY/gi, hi: "कपास परीक्षण एवं अनुसंधान प्रयोगशाला", ta: "பருத்தி சோதனை மற்றும் ஆராய்ச்சி ஆய்வகம்" },
  { en: /BUREAU OF INDIAN STANDARDS/gi, hi: "भारतीय मानक ब्यूरो (BIS)", ta: "இந்திய தரநிலைகள் பணியகம் (BIS)" },
  { en: /CENTRAL POWER RESEARCH INSTITUTE/gi, hi: "केंद्रीय विद्युत अनुसंधान संस्थान (CPRI)", ta: "மத்திய மின் ஆராய்ச்சி நிறுவனம் (CPRI)" },
  { en: /ELECTRICAL RESEARCH AND DEVELOPMENT ASSOCIATION/gi, hi: "विद्युत अनुसंधान एवं विकास संघ (ERDA)", ta: "மின் ஆராய்ச்சி மற்றும் மேம்பாட்டு சங்கம் (ERDA)" },
  { en: /ELECTRONICS REGIONAL TEST LABORATORY/gi, hi: "इलेक्ट्रॉनिक्स क्षेत्रीय परीक्षण प्रयोगशाला (ERTL)", ta: "மின்னணுவியல் பிராந்திய சோதனை ஆய்வகம் (ERTL)" },
  { en: /NATIONAL TEST HOUSE/gi, hi: "राष्ट्रीय परीक्षण गृह (NTH)", ta: "தேசிய சோதனை இல்லம் (NTH)" },
  { en: /INDIAN OIL CORPORATION LIMITED/gi, hi: "इंडियन ऑयल कॉर्पोरेशन लिमिटेड (IOCL)", ta: "இந்தியன் ஆயில் கார்ப்பரேஷன் லிமிடெட் (IOCL)" },
  { en: /INDIAN OIL CORPORATION LTD\.?/gi, hi: "इंडियन ऑयल कॉर्पोरेशन लिमिटेड (IOCL)", ta: "இந்தியன் ஆயில் கார்ப்பரேஷன் லிமிடெட் (IOCL)" },
  { en: /\bIOCL\b/gi, hi: "इंडियन ऑयल (IOCL)", ta: "இந்தியன் ஆயில் (IOCL)" },
  { en: /CENTRAL INSTITUTE OF PETROCHEMICALS ENGINEERING & TECHNOLOGY/gi, hi: "केंद्रीय पेट्रोकेमिकल्स इंजीनियरिंग एवं प्रौद्योगिकी संस्थान (CIPET)", ta: "மத்திய பெட்ரோகெமிக்கல்ஸ் பொறியியல் மற்றும் தொழில்நுட்ப நிறுவனம் (CIPET)" },
  { en: /CENTRAL INSTITUTE OF PETROCHEMICALS ENGINEERING AND TECHNOLOGY/gi, hi: "केंद्रीय पेट्रोकेमिकल्स इंजीनियरिंग एवं प्रौद्योगिकी संस्थान (CIPET)", ta: "மத்திய பெட்ரோகெமிக்கல்ஸ் பொறியியல் மற்றும் தொழில்நுட்ப நிறுவனம் (CIPET)" },
  { en: /CENTRAL INSTITUTE OF PLASTICS ENGINEERING & TECHNOLOGY/gi, hi: "केंद्रीय प्लास्टिक इंजीनियरिंग एवं प्रौद्योगिकी संस्थान (CIPET)", ta: "மத்திய பிளாஸ்டிக் பொறியியல் மற்றும் தொழில்நுட்ப நிறுவனம் (CIPET)" },
  { en: /\bCIPET\b/gi, hi: "सीपेट (CIPET)", ta: "சிபெட் (CIPET)" },
  { en: /FOOTWEAR DESIGN AND DEVELOPMENT INSTITUTE/gi, hi: "फुटवियर डिजाइन एवं विकास संस्थान (FDDI)", ta: "காலணி வடிவமைப்பு மற்றும் மேம்பாட்டு நிறுவனம் (FDDI)" },
  { en: /SHRIRAM INSTITUTE FOR INDUSTRIAL RESEARCH/gi, hi: "श्रीराम औद्योगिक अनुसंधान संस्थान", ta: "ஸ்ரீராம் தொழில்துறை ஆராய்ச்சி நிறுவனம்" },
  { en: /INSTITUTE FOR INDUSTRIAL RESEARCH/gi, hi: "औद्योगिक अनुसंधान संस्थान", ta: "தொழில்துறை ஆராய்ச்சி நிறுவனம்" },
  { en: /WAKEFIELD INSPECTION SERVICES INDIA/gi, hi: "वेकफील्ड इंस्पेक्शन सर्विसेज इंडिया", ta: "வேக்ஃபீல்ட் இன்ஸ்பெக்ஷன் சர்வீசஸ் இந்தியா" },
  { en: /WAKEFIELD INSPECTION SERVICES/gi, hi: "वेकफील्ड इंस्पेक्शन सर्विसेज", ta: "வேக்ஃபீல்ட் இன்ஸ்பெக்ஷன் சர்வீசஸ்" },
  { en: /NATIONAL RESEARCH AND TECHNOLOGY CONSORTIUM/gi, hi: "राष्ट्रीय अनुसंधान एवं प्रौद्योगिकी संघ (NRTC)", ta: "தேசிய ஆராய்ச்சி மற்றும் தொழில்நுட்ப கூட்டமைப்பு (NRTC)" },
  { en: /INSTITUTE OF SECONDARY STEEL TECHNOLOGY/gi, hi: "द्वितीयक इस्पात प्रौद्योगिकी संस्थान", ta: "இரண்டாம் நிலை எஃகு தொழில்நுட்ப நிறுவனம்" },
  { en: /INSTITUTE FOR AUTO PARTS AND HAND TOOLS TECHNOLOGY/gi, hi: "ऑटो पार्ट्स एवं हैंड टूल्स प्रौद्योगिकी संस्थान", ta: "வாகன பாகங்கள் மற்றும் கை கருவிகள் தொழில்நுட்ப நிறுவனம்" },

  // Specialized Lab Units
  { en: /ELECTRO MAGNETIC LABORATORY/gi, hi: "इलेक्ट्रो मैग्नेटिक प्रयोगशाला", ta: "மின்காந்த ஆய்வகம்" },
  { en: /ELECTRICAL TESTING AND RESEARCH LABORATORY/gi, hi: "विद्युत परीक्षण एवं अनुसंधान प्रयोगशाला", ta: "மின் சோதனை மற்றும் ஆராய்ச்சி ஆய்வகம்" },
  { en: /ELECTRICAL TESTING & RESEARCH LABORATORY/gi, hi: "विद्युत परीक्षण एवं अनुसंधान प्रयोगशाला", ta: "மின் சோதனை மற்றும் ஆராய்ச்சி ஆய்வகம்" },
  { en: /ELECTRONICS TESTING CENTRE/gi, hi: "इलेक्ट्रॉनिक्स परीक्षण केंद्र", ta: "மின்னணுவியல் சோதனை மையம்" },
  { en: /ELECTRONICS TESTING CENTER/gi, hi: "इलेक्ट्रॉनिक्स परीक्षण केंद्र", ta: "மின்னணுவியல் சோதனை மையம்" },
  { en: /COMPLIANCE AND TESTING LABORATORIES/gi, hi: "अनुपालन एवं परीक्षण प्रयोगशालाएं", ta: "இணக்கம் மற்றும் சோதனை ஆய்வகங்கள்" },
  { en: /COMPLIANCE & TESTING LABORATORIES/gi, hi: "अनुपालन एवं परीक्षण प्रयोगशालाएं", ta: "இணக்கம் மற்றும் சோதனை ஆய்வகங்கள்" },
  { en: /FOOD RESEARCH & ANALYSIS CENTRE/gi, hi: "खाद्य अनुसंधान एवं विश्लेषण केंद्र", ta: "உணவு ஆராய்ச்சி மற்றும் பகுப்பாய்வு மையம்" },
  { en: /FOOD RESEARCH AND ANALYSIS CENTRE/gi, hi: "खाद्य अनुसंधान एवं विश्लेषण केंद्र", ta: "உணவு ஆராய்ச்சி மற்றும் பகுப்பாய்வு மையம்" },
  { en: /QUALITY CERTIFICATIONS/gi, hi: "गुणवत्ता प्रमाणन", ta: "தர சான்றிதழ்" },
  { en: /CENTRAL REGIONAL OFFICE & LABORATORY/gi, hi: "केंद्रीय क्षेत्रीय कार्यालय एवं प्रयोगशाला", ta: "மத்திய பிராந்திய அலுவலகம் மற்றும் ஆய்வகம்" },
  { en: /CENTRAL REGIONAL OFFICE AND LABORATORY/gi, hi: "केंद्रीय क्षेत्रीय कार्यालय एवं प्रयोगशाला", ta: "மத்திய பிராந்திய அலுவலகம் एवं ஆய்வகம்" },
  { en: /CENTRAL LABORATORY/gi, hi: "केंद्रीय प्रयोगशाला", ta: "மத்திய ஆய்வகம்" },
  { en: /WESTERN REGIONAL LABORATORY/gi, hi: "पश्चिमी क्षेत्रीय प्रयोगशाला", ta: "மேற்கு மண்டல ஆய்வகம்" },
  { en: /SOUTHERN REGIONAL LABORATORY/gi, hi: "दक्षिणी क्षेत्रीय प्रयोगशाला", ta: "தெற்கு மண்டல ஆய்வகம்" },
  { en: /EASTERN REGIONAL LABORATORY/gi, hi: "पूर्वी क्षेत्रीय प्रयोगशाला", ta: "கிழக்கு மண்டல ஆய்வகம்" },
  { en: /NORTHERN REGIONAL LABORATORY/gi, hi: "उत्तरी क्षेत्रीय प्रयोगशाला", ta: "வடக்கு மண்டல ஆய்வகம்" },
  { en: /TEXTILE COMMITTEE QUALITY ASSURANCE LABORATORY/gi, hi: "वस्त्र समिति गुणवत्ता आश्वासन प्रयोगशाला", ta: "ஜவுளிக் குழும தர உத்தரவாத ஆய்வகம்" },
  { en: /QUALITY ASSURANCE LABORATORY/gi, hi: "गुणवत्ता आश्वासन प्रयोगशाला", ta: "தர உத்தரவாத ஆய்வகம்" },
  { en: /TESTING AND RESEARCH LABORATORY/gi, hi: "परीक्षण एवं अनुसंधान प्रयोगशाला", ta: "சோதனை மற்றும் ஆராய்ச்சி ஆய்வகம்" },
  { en: /TESTING & RESEARCH LABORATORY/gi, hi: "परीक्षण एवं अनुसंधान प्रयोगशाला", ta: "சோதனை மற்றும் ஆராய்ச்சி ஆய்வகம்" },
  { en: /TEST AND RESEARCH CENTRE/gi, hi: "परीक्षण एवं अनुसंधान केंद्र", ta: "சோதனை மற்றும் ஆராய்ச்சி மையம்" },
  { en: /TEST & RESEARCH CENTRE/gi, hi: "परीक्षण एवं अनुसंधान केंद्र", ta: "சோதனை மற்றும் ஆராய்ச்சி மையம்" },
  { en: /RESEARCH AND DEVELOPMENT CENTRE/gi, hi: "अनुसंधान एवं विकास केंद्र", ta: "ஆராய்ச்சி மற்றும் மேம்பாட்டு மையம்" },
  { en: /RESEARCH & DEVELOPMENT CENTRE/gi, hi: "अनुसंधान एवं विकास केंद्र", ta: "ஆராய்ச்சி மற்றும் மேம்பாட்டு மையம்" },
  { en: /RESEARCH AND DEVELOPMENT/gi, hi: "अनुसंधान एवं विकास", ta: "ஆராய்ச்சி மற்றும் மேம்பாடு" },
  { en: /RESEARCH & DEVELOPMENT/gi, hi: "अनुसंधान एवं विकास", ta: "ஆராய்ச்சி மற்றும் மேம்பாடு" },
  { en: /CALIBRATION AND TESTING LABORATORY/gi, hi: "अंशांकन एवं परीक्षण प्रयोगशाला", ta: "அளவுத்திருத்தம் மற்றும் சோதனை ஆய்வகம்" },
  { en: /ANALYTICAL AND RESEARCH/gi, hi: "विश्लेषणात्मक एवं अनुसंधान", ta: "பகுப்பாய்வு மற்றும் ஆராய்ச்சி" },
  { en: /ENVIRONMENTAL LABORATORY/gi, hi: "पर्यावरण प्रयोगशाला", ta: "சுற்றுச்சூழல் ஆய்வகம்" },
  { en: /TESTING LABORATORY/gi, hi: "परीक्षण प्रयोगशाला", ta: "சோதனை ஆய்வகம்" },
  { en: /TESTING LABORATORIES/gi, hi: "परीक्षण प्रयोगशालाएं", ta: "சோதனை ஆய்வகங்கள்" },
  { en: /TESTING FACILITY/gi, hi: "परीक्षण सुविधा", ta: "சோதனை மையம்" },
  { en: /TEST LABORATORY/gi, hi: "परीक्षण प्रयोगशाला", ta: "சோதனை ஆய்வகம்" },
  { en: /TEST HOUSE/gi, hi: "परीक्षण गृह", ta: "சோதனை இல்லம்" },
  { en: /ANALYTICAL LABORATORY/gi, hi: "विश्लेषणात्मक प्रयोगशाला", ta: "பகுப்பாய்வு ஆய்வகம்" },
  { en: /STANDARDS LABORATORY/gi, hi: "मानक प्रयोगशाला", ta: "தரநிலை ஆய்வகம்" },
  { en: /RESEARCH INSTITUTE/gi, hi: "अनुसंधान संस्थान", ta: "ஆராய்ச்சி நிறுவனம்" },
  { en: /RESEARCH CENTRE/gi, hi: "अनुसंधान केंद्र", ta: "ஆராய்ச்சி மையம்" },
  { en: /RESEARCH CENTER/gi, hi: "अनुसंधान केंद्र", ta: "ஆராய்ச்சி மையம்" },
  { en: /TESTING CENTRE/gi, hi: "परीक्षण केंद्र", ta: "சோதனை மையம்" },
  { en: /TESTING CENTER/gi, hi: "परीक्षण केंद्र", ta: "சோதனை மையம்" },
  { en: /FOOD LABORATORY/gi, hi: "खाद्य प्रयोगशाला", ta: "உணவு ஆய்வகம்" },
  { en: /REGIONAL LABORATORY/gi, hi: "क्षेत्रीय प्रयोगशाला", ta: "பிராந்திய ஆய்வகம்" },
  { en: /A UNIT OF/gi, hi: "की एक इकाई", ta: "இன் ஒரு பிரிவு" },
  { en: /LABORATORIES/gi, hi: "प्रयोगशालाएं", ta: "ஆய்வகங்கள்" },
  { en: /LABORATORY/gi, hi: "प्रयोगशाला", ta: "ஆய்வகம்" },

  // Geographic Regions
  { en: /\(SOUTHERN REGION\)/gi, hi: "(दक्षिणी क्षेत्र)", ta: "(தென் மண்டலம்)" },
  { en: /\(WESTERN REGION\)/gi, hi: "(पश्चिमी क्षेत्र)", ta: "(மேற்கு மண்டலம்)" },
  { en: /\(EASTERN REGION\)/gi, hi: "(पूर्वी क्षेत्र)", ta: "(கிழக்கு மண்டலம்)" },
  { en: /\(NORTHERN REGION\)/gi, hi: "(उत्तरी क्षेत्र)", ta: "(வட மண்டலம்)" },
  { en: /\(ERTL NORTH\)/gi, hi: "(ईआरटीएल उत्तर)", ta: "(ERTL வடக்கு)" },
  { en: /\(ERTL SOUTH\)/gi, hi: "(ईआरटीएल दक्षिण)", ta: "(ERTL தெற்கு)" },
  { en: /\(ERTL EAST\)/gi, hi: "(ईआरटीएल पूर्व)", ta: "(ERTL கிழக்கு)" },
  { en: /\(ERTL WEST\)/gi, hi: "(ईआरटीएल पश्चिम)", ta: "(ERTL மேற்கு)" },

  // Corporate Entities
  { en: /PVT\.?\s*LTD\.?/gi, hi: "प्राइवेट लिमिटेड", ta: "பிரைவேட் லிமிடெட்" },
  { en: /PRIVATE LIMITED/gi, hi: "प्राइवेट लिमिटेड", ta: "பிரைவேட் லிமிடெட்" },
  { en: /\bLLP\b/gi, hi: "एलएलपी", ta: "எல்எல்பி" },
  { en: /LTD\.?/gi, hi: "लिमिटेड", ta: "லிமிடெட்" },
  { en: /LIMITED/gi, hi: "लिमिटेड", ta: "லிமிடெட்" },
  { en: /SOUTH ASIA/gi, hi: "साउथ एशिया", ta: "தெற்காசியா" },
  { en: /TUV SUD/gi, hi: "टीयूवी एसयूडी", ta: "டியூவி எஸ்யுடி" },
  { en: /TUV RHEINLAND/gi, hi: "टीयूवी राइनलैंड", ta: "டியூவி ரைன்லாந்து" },
  { en: /BUREAU VERITAS/gi, hi: "ब्यूरो वेरिटास", ta: "பியூரோ வெரிடாஸ்" },
  { en: /INTERTEK INDIA/gi, hi: "इंटरटेक इंडिया", ta: "இன்டர்டெக் இந்தியா" },
  { en: /INTERTEK/gi, hi: "इंटरटेक", ta: "இன்டர்டெக்" },
  { en: /UL INDIA/gi, hi: "यूएल इंडिया", ta: "யுஎல் இந்தியா" },
  { en: /SGS INDIA/gi, hi: "एसजीएस इंडिया", ta: "எஸ்ஜிஎஸ் இந்தியா" },
  { en: /EUROFINS/gi, hi: "यूरोफिन्स", ta: "யூரோபின்ஸ்" },
  { en: /DEKRA/gi, hi: "डेक्रा", ta: "டெக்ரா" },
  { en: /ITC LIMITED/gi, hi: "आईटीसी लिमिटेड", ta: "ஐடிசி லிமிடெட்" },
  { en: /\bBIS\b/g, hi: "बीआईएस", ta: "BIS" },
];

/**
 * Localizes a laboratory name into Hindi or Tamil.
 * Returns the localized name if language is 'hi' or 'ta', otherwise returns original.
 */
export function localizeLabName(rawName: string, language: string): string {
  if (!rawName || (language !== "hi" && language !== "ta")) {
    return rawName;
  }

  const lang = language as "hi" | "ta";
  let localized = rawName;

  // 1. Replace institutional and laboratory phrases
  for (const item of PHRASE_DICTIONARY) {
    localized = localized.replace(item.en, item[lang]);
  }

  // 2. Localize city names present in the laboratory name (e.g. ", AHMEDABAD")
  for (const [cityKey, cityTrans] of Object.entries(CITY_LOCALIZATION)) {
    const cityRegex = new RegExp(`\\b${cityKey}\\b`, "gi");
    localized = localized.replace(cityRegex, cityTrans[lang]);
  }

  return localized;
}

/**
 * Localizes city name into target language.
 */
export function localizeCity(city: string | undefined, language: string): string {
  if (!city) return "";
  if (language !== "hi" && language !== "ta") return city;
  const key = city.trim().toLowerCase();
  const trans = CITY_LOCALIZATION[key];
  return trans ? trans[language as "hi" | "ta"] : city;
}

/**
 * Localizes state name into target language.
 */
export function localizeState(state: string | undefined, language: string): string {
  if (!state) return "";
  if (language !== "hi" && language !== "ta") return state;
  const key = state.trim().toLowerCase();
  const trans = STATE_LOCALIZATION[key];
  return trans ? trans[language as "hi" | "ta"] : state;
}

/**
 * Localizes laboratory testing scope summary into target language.
 */
export function localizeTestingScope(summary: string | undefined, language: string): string {
  if (!summary || (language !== "hi" && language !== "ta")) {
    return summary || "";
  }

  const isHi = language === "hi";

  // Common BIS testing scope sentences
  if (summary.includes("Safety, electromagnetic compatibility (EMC), and performance testing")) {
    return isHi
      ? "आईटी उपकरण, उपभोक्ता इलेक्ट्रॉनिक्स, एलईडी ड्राइवर, पावर एडेप्टर और सेकेंडरी लिथियम बैटरी के लिए सुरक्षा, विद्युत चुम्बकीय अनुकूलता (EMC) और प्रदर्शन परीक्षण।"
      : "தகவல் தொழில்நுட்ப சாதனங்கள், நுகர்வோர் மின்னணுவியல், LED டிரைவர்கள், பவர் அடாப்டர்கள் மற்றும் இரண்டாம் நிலை லித்தியம் பேட்டரிகளுக்கான பாதுகாப்பு, மின்காந்த இணக்கத்தன்மை (EMC) மற்றும் செயல்திறன் சோதனை.";
  }

  if (summary.includes("Apex national testing facility")) {
    return isHi
      ? "विद्युत उपकरणों, रासायनिक विश्लेषण, मैकेनिकल इंजीनियरिंग, प्लास्टिक, पैकेजिंग और खाद्य सुरक्षा के लिए शीर्ष राष्ट्रीय परीक्षण सुविधा।"
      : "மின் சாதனங்கள், வேதியியல் பகுப்பாய்வு, மெக்கானிக்கல் இன்ஜினியரிங், பிளாஸ்டிக், பேக்கேஜிங் மற்றும் உணவுப் பாதுகாப்புக்கான முதன்மை தேசிய சோதனை மையம்.";
  }

  if (summary.includes("Western regional testing facility")) {
    return isHi
      ? "उपभोक्ता उपकरणों, प्लास्टिक, धातुकर्म, रसायनों और घरेलू विद्युत उपकरणों के लिए पश्चिमी क्षेत्रीय परीक्षण केंद्र।"
      : "நுகர்வோர் சாதனங்கள், பிளாஸ்டிக், உலோகவியல், இரசாயனங்கள் மற்றும் வீட்டு மின் சாதனங்களுக்கான மேற்கு மண்டல சோதனை மையம்.";
  }

  if (summary.includes("Southern regional testing facility")) {
    return isHi
      ? "विद्युत इन्सुलेशन, केबल, ट्रांसफार्मर, खाद्य तेल और पेय पदार्थों के लिए दक्षिणी क्षेत्रीय परीक्षण केंद्र।"
      : "மின் காப்பு, கேபிள்கள், மின்மாற்றிகள், சமையல் எண்ணெய் மற்றும் பானங்களுக்கான தென் மண்டல சோதனை மையம்.";
  }

  if (summary.includes("Eastern regional testing facility")) {
    return isHi
      ? "धातुकर्म परीक्षण, विद्युत सुरक्षा, पंखे, पैकेजिंग और रसायनों के लिए पूर्वी क्षेत्रीय परीक्षण केंद्र।"
      : "உலோகவியல் சோதனை, மின் பாதுகாப்பு, விசிறிகள், பேக்கேஜிங் மற்றும் இரசாயனங்களுக்கான கிழக்கு மண்டல சோதனை மையம்.";
  }

  if (summary.includes("Northern regional laboratory")) {
    return isHi
      ? "कृषि मशीनरी, खाद्य उत्पाद, पंप, मोटर और इलेक्ट्रो-तकनीकी वस्तुओं के लिए उत्तरी क्षेत्रीय परीक्षण प्रयोगशाला।"
      : "விவசாய இயந்திரங்கள், உணவுப் பொருட்கள், பம்புகள், மோட்டார்கள் மற்றும் மின் தொழில்நுட்ப பொருட்களுக்கான வடக்கு மண்டல சோதனை ஆய்வகம்.";
  }

  if (summary.includes("Central regional facility")) {
    return isHi
      ? "रासायनिक परीक्षण, निर्माण सामग्री, कृषि उपकरण और बोतलबंद पानी के लिए केंद्रीय क्षेत्रीय सुविधा।"
      : "இரசாயன சோதனை, கட்டுமானப் பொருட்கள், விவசாய உபகரணங்கள் மற்றும் பாட்டில் தண்ணீருக்கான மத்திய மண்டல வசதி.";
  }

  if (summary.includes("Conformity testing and quality evaluation facility recognized under BIS LIMS")) {
    return isHi
      ? "बीआईएस एलआईएमएस / प्रयोगशाला मान्यता योजना के तहत मान्यता प्राप्त अनुरूपता परीक्षण एवं गुणवत्ता मूल्यांकन सुविधा।"
      : "BIS LIMS / ஆய்வக அங்கீகாரத் திட்டத்தின் கீழ் அங்கீகரிக்கப்பட்ட இணக்க சோதனை மற்றும் தர மதிப்பீட்டு வசதி.";
  }

  return summary;
}

/**
 * Localizes laboratory recognition badge text into target language.
 */
export function localizeRecognitionBadge(type: string, language: string): { label: string; className: string } {
  const isHi = language === "hi";
  const isTa = language === "ta";

  switch (type) {
    case "BIS_CENTRAL":
      return {
        label: isHi ? "बीआईएस केंद्रीय शीर्ष प्रयोगशाला" : isTa ? "BIS மத்திய முதன்மை ஆய்வகம்" : "BIS Apex Central Lab",
        className: "bg-purple-50 text-purple-700 border-purple-200",
      };
    case "BIS_BRANCH":
      return {
        label: isHi ? "बीआईएस क्षेत्रीय प्रयोगशाला" : isTa ? "BIS பிராந்திய ஆய்வகம்" : "BIS Regional Lab",
        className: "bg-indigo-50 text-indigo-700 border-indigo-200",
      };
    case "BIS_RECOGNIZED":
      return {
        label: isHi ? "बीआईएस मान्यता प्राप्त (LIMS)" : isTa ? "BIS அங்கீகரிக்கப்பட்டது (LIMS)" : "BIS Recognized (LIMS)",
        className: "bg-blue-50 text-blue-700 border-blue-200",
      };
    case "BIS_EMPANELLED":
      return {
        label: isHi ? "बीआईएस सूचीबद्ध प्रयोगशाला" : isTa ? "BIS பட்டியலிடப்பட்ட ஆய்வகம்" : "BIS Empanelled",
        className: "bg-amber-50 text-amber-800 border-amber-200",
      };
    case "NABL_ACCREDITED":
      return {
        label: isHi ? "एनएबीएल मान्यता प्राप्त केंद्र" : isTa ? "NABL அங்கீகரிக்கப்பட்ட மையம்" : "NABL Accredited",
        className: "bg-emerald-50 text-emerald-700 border-emerald-200",
      };
    default:
      return {
        label: type.replace(/_/g, " "),
        className: "bg-slate-50 text-slate-700 border-slate-200",
      };
  }
}
