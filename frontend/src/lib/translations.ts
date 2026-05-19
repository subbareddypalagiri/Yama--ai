// Multi-language translations for YAMA AI Legal Platform
// Supports: English, Hindi, Tamil, Telugu

export type Language = 'en' | 'hi' | 'ta' | 'te';

export const languageNames: Record<Language, string> = {
  en: 'English',
  hi: 'हिंदी',
  ta: 'தமிழ்',
  te: 'తెలుగు'
};

export const translations = {
  en: {
    // Navigation
    nav: {
      home: 'Home',
      chat: 'AI Chat',
      cases: 'My Cases',
      about: 'About',
      contact: 'Contact',
      login: 'Login',
      signup: 'Sign Up'
    },
    // Hero Section
    hero: {
      title: 'YAMA AI',
      subtitle: 'Your Legal Intelligence',
      tagline: 'AI-Powered Legal Analysis for Indian Law',
      cta: 'Start Analysis',
      openChat: 'Open Chat'
    },
    // Features
    features: {
      title: 'Features',
      legalAnalysis: 'Legal Analysis',
      legalAnalysisDesc: 'Get instant AI-powered analysis of your legal situations',
      caseTracking: 'Case Tracking',
      caseTrackingDesc: 'Track and manage all your legal cases in one place',
      documentUpload: 'Document Upload',
      documentUploadDesc: 'Upload and analyze legal documents with AI',
      pdfExport: 'PDF Export',
      pdfExportDesc: 'Generate professional legal reports and summaries'
    },
    // Chat
    chat: {
      placeholder: 'Describe your legal situation...',
      send: 'Send',
      thinking: 'AI is analyzing...',
      welcome: 'Hello! I am YAMA AI, your legal assistant. How can I help you today?',
      error: 'Something went wrong. Please try again.'
    },
    // Cases
    cases: {
      title: 'My Cases',
      newCase: 'New Case',
      allCases: 'All Cases',
      active: 'Active',
      pending: 'Pending',
      resolved: 'Resolved',
      closed: 'Closed',
      draft: 'Draft',
      search: 'Search cases...',
      noResults: 'No cases found',
      createCase: 'Create New Case',
      caseTitle: 'Case Title',
      description: 'Description',
      status: 'Status',
      priority: 'Priority',
      high: 'High',
      medium: 'Medium',
      low: 'Low',
      documents: 'Documents',
      timeline: 'Timeline',
      overview: 'Overview',
      uploadDoc: 'Upload Document',
      exportPdf: 'Export PDF',
      addEvent: 'Add Event',
      created: 'Created',
      updated: 'Updated'
    },
    // Common
    common: {
      save: 'Save',
      cancel: 'Cancel',
      delete: 'Delete',
      edit: 'Edit',
      view: 'View',
      download: 'Download',
      upload: 'Upload',
      loading: 'Loading...',
      success: 'Success!',
      error: 'Error',
      confirm: 'Confirm',
      back: 'Back',
      next: 'Next',
      submit: 'Submit',
      close: 'Close'
    },
    // Footer
    footer: {
      rights: 'All rights reserved',
      privacy: 'Privacy Policy',
      terms: 'Terms of Service',
      madeWith: 'Made with ❤️ in India'
    }
  },
  hi: {
    // Navigation
    nav: {
      home: 'होम',
      chat: 'AI चैट',
      cases: 'मेरे केस',
      about: 'हमारे बारे में',
      contact: 'संपर्क करें',
      login: 'लॉगिन',
      signup: 'साइन अप'
    },
    // Hero Section
    hero: {
      title: 'यम AI',
      subtitle: 'आपकी कानूनी बुद्धिमत्ता',
      tagline: 'भारतीय कानून के लिए AI-संचालित कानूनी विश्लेषण',
      cta: 'विश्लेषण शुरू करें',
      openChat: 'चैट खोलें'
    },
    // Features
    features: {
      title: 'विशेषताएं',
      legalAnalysis: 'कानूनी विश्लेषण',
      legalAnalysisDesc: 'अपनी कानूनी स्थितियों का तुरंत AI-संचालित विश्लेषण प्राप्त करें',
      caseTracking: 'केस ट्रैकिंग',
      caseTrackingDesc: 'अपने सभी कानूनी मामलों को एक स्थान पर ट्रैक और प्रबंधित करें',
      documentUpload: 'दस्तावेज़ अपलोड',
      documentUploadDesc: 'AI के साथ कानूनी दस्तावेज़ अपलोड और विश्लेषण करें',
      pdfExport: 'PDF निर्यात',
      pdfExportDesc: 'पेशेवर कानूनी रिपोर्ट और सारांश उत्पन्न करें'
    },
    // Chat
    chat: {
      placeholder: 'अपनी कानूनी स्थिति का वर्णन करें...',
      send: 'भेजें',
      thinking: 'AI विश्लेषण कर रहा है...',
      welcome: 'नमस्ते! मैं यम AI हूं, आपका कानूनी सहायक। आज मैं आपकी कैसे मदद कर सकता हूं?',
      error: 'कुछ गलत हो गया। कृपया पुनः प्रयास करें।'
    },
    // Cases
    cases: {
      title: 'मेरे केस',
      newCase: 'नया केस',
      allCases: 'सभी केस',
      active: 'सक्रिय',
      pending: 'लंबित',
      resolved: 'हल किया गया',
      closed: 'बंद',
      draft: 'ड्राफ्ट',
      search: 'केस खोजें...',
      noResults: 'कोई केस नहीं मिला',
      createCase: 'नया केस बनाएं',
      caseTitle: 'केस शीर्षक',
      description: 'विवरण',
      status: 'स्थिति',
      priority: 'प्राथमिकता',
      high: 'उच्च',
      medium: 'मध्यम',
      low: 'निम्न',
      documents: 'दस्तावेज़',
      timeline: 'समयरेखा',
      overview: 'अवलोकन',
      uploadDoc: 'दस्तावेज़ अपलोड करें',
      exportPdf: 'PDF निर्यात करें',
      addEvent: 'इवेंट जोड़ें',
      created: 'बनाया गया',
      updated: 'अपडेट किया गया'
    },
    // Common
    common: {
      save: 'सहेजें',
      cancel: 'रद्द करें',
      delete: 'हटाएं',
      edit: 'संपादित करें',
      view: 'देखें',
      download: 'डाउनलोड',
      upload: 'अपलोड',
      loading: 'लोड हो रहा है...',
      success: 'सफलता!',
      error: 'त्रुटि',
      confirm: 'पुष्टि करें',
      back: 'वापस',
      next: 'अगला',
      submit: 'जमा करें',
      close: 'बंद करें'
    },
    // Footer
    footer: {
      rights: 'सर्वाधिकार सुरक्षित',
      privacy: 'गोपनीयता नीति',
      terms: 'सेवा की शर्तें',
      madeWith: 'भारत में ❤️ के साथ बनाया गया'
    }
  },
  ta: {
    // Navigation
    nav: {
      home: 'முகப்பு',
      chat: 'AI அரட்டை',
      cases: 'என் வழக்குகள்',
      about: 'எங்களைப் பற்றி',
      contact: 'தொடர்பு',
      login: 'உள்நுழை',
      signup: 'பதிவு செய்'
    },
    // Hero Section
    hero: {
      title: 'யம AI',
      subtitle: 'உங்கள் சட்ட நுண்ணறிவு',
      tagline: 'இந்திய சட்டத்திற்கான AI-இயக்கும் சட்ட பகுப்பாய்வு',
      cta: 'பகுப்பாய்வைத் தொடங்கு',
      openChat: 'அரட்டை திற'
    },
    // Features
    features: {
      title: 'அம்சங்கள்',
      legalAnalysis: 'சட்ட பகுப்பாய்வு',
      legalAnalysisDesc: 'உங்கள் சட்ட சூழ்நிலைகளின் உடனடி AI-இயக்கும் பகுப்பாய்வைப் பெறுங்கள்',
      caseTracking: 'வழக்கு கண்காணிப்பு',
      caseTrackingDesc: 'உங்கள் அனைத்து சட்ட வழக்குகளையும் ஒரே இடத்தில் கண்காணித்து நிர்வகிக்கவும்',
      documentUpload: 'ஆவண பதிவேற்றம்',
      documentUploadDesc: 'AI உடன் சட்ட ஆவணங்களை பதிவேற்றி பகுப்பாய்வு செய்யுங்கள்',
      pdfExport: 'PDF ஏற்றுமதி',
      pdfExportDesc: 'தொழில்முறை சட்ட அறிக்கைகள் மற்றும் சுருக்கங்களை உருவாக்குங்கள்'
    },
    // Chat
    chat: {
      placeholder: 'உங்கள் சட்ட நிலையை விவரிக்கவும்...',
      send: 'அனுப்பு',
      thinking: 'AI பகுப்பாய்வு செய்கிறது...',
      welcome: 'வணக்கம்! நான் யம AI, உங்கள் சட்ட உதவியாளர். இன்று நான் உங்களுக்கு எப்படி உதவ முடியும்?',
      error: 'ஏதோ தவறு நடந்தது. மீண்டும் முயற்சிக்கவும்.'
    },
    // Cases
    cases: {
      title: 'என் வழக்குகள்',
      newCase: 'புதிய வழக்கு',
      allCases: 'அனைத்து வழக்குகள்',
      active: 'செயலில்',
      pending: 'நிலுவையில்',
      resolved: 'தீர்க்கப்பட்டது',
      closed: 'மூடப்பட்டது',
      draft: 'வரைவு',
      search: 'வழக்குகளைத் தேடு...',
      noResults: 'வழக்குகள் இல்லை',
      createCase: 'புதிய வழக்கை உருவாக்கு',
      caseTitle: 'வழக்கு தலைப்பு',
      description: 'விவரம்',
      status: 'நிலை',
      priority: 'முன்னுரிமை',
      high: 'உயர்',
      medium: 'நடுத்தர',
      low: 'குறை',
      documents: 'ஆவணங்கள்',
      timeline: 'காலவரிசை',
      overview: 'மேலோட்டம்',
      uploadDoc: 'ஆவணத்தைப் பதிவேற்று',
      exportPdf: 'PDF ஏற்றுமதி',
      addEvent: 'நிகழ்வைச் சேர்',
      created: 'உருவாக்கப்பட்டது',
      updated: 'புதுப்பிக்கப்பட்டது'
    },
    // Common
    common: {
      save: 'சேமி',
      cancel: 'ரத்து செய்',
      delete: 'நீக்கு',
      edit: 'திருத்து',
      view: 'பார்',
      download: 'பதிவிறக்கு',
      upload: 'பதிவேற்று',
      loading: 'ஏற்றுகிறது...',
      success: 'வெற்றி!',
      error: 'பிழை',
      confirm: 'உறுதிப்படுத்து',
      back: 'பின்',
      next: 'அடுத்து',
      submit: 'சமர்ப்பி',
      close: 'மூடு'
    },
    // Footer
    footer: {
      rights: 'அனைத்து உரிமைகளும் பாதுகாக்கப்பட்டவை',
      privacy: 'தனியுரிமைக் கொள்கை',
      terms: 'சேவை விதிமுறைகள்',
      madeWith: 'இந்தியாவில் ❤️ உடன் உருவாக்கப்பட்டது'
    }
  },
  te: {
    // Navigation
    nav: {
      home: 'హోమ్',
      chat: 'AI చాట్',
      cases: 'నా కేసులు',
      about: 'మా గురించి',
      contact: 'సంప్రదించండి',
      login: 'లాగిన్',
      signup: 'సైన్ అప్'
    },
    // Hero Section
    hero: {
      title: 'యమ AI',
      subtitle: 'మీ చట్టపరమైన తెలివితేటలు',
      tagline: 'భారతీయ చట్టం కోసం AI-ఆధారిత చట్టపరమైన విశ్లేషణ',
      cta: 'విశ్లేషణ ప్రారంభించండి',
      openChat: 'చాట్ తెరవండి'
    },
    // Features
    features: {
      title: 'ఫీచర్లు',
      legalAnalysis: 'చట్టపరమైన విశ్లేషణ',
      legalAnalysisDesc: 'మీ చట్టపరమైన పరిస్థితుల తక్షణ AI-ఆధారిత విశ్లేషణ పొందండి',
      caseTracking: 'కేసు ట్రాకింగ్',
      caseTrackingDesc: 'మీ అన్ని చట్టపరమైన కేసులను ఒకే చోట ట్రాక్ చేసి నిర్వహించండి',
      documentUpload: 'డాక్యుమెంట్ అప్‌లోడ్',
      documentUploadDesc: 'AI తో చట్టపరమైన పత్రాలను అప్‌లోడ్ చేసి విశ్లేషించండి',
      pdfExport: 'PDF ఎగుమతి',
      pdfExportDesc: 'ప్రొఫెషనల్ చట్టపరమైన నివేదికలు మరియు సారాంశాలను రూపొందించండి'
    },
    // Chat
    chat: {
      placeholder: 'మీ చట్టపరమైన పరిస్థితిని వివరించండి...',
      send: 'పంపండి',
      thinking: 'AI విశ్లేషిస్తోంది...',
      welcome: 'నమస్కారం! నేను యమ AI, మీ చట్టపరమైన సహాయకుడిని. ఈరోజు నేను మీకు ఎలా సహాయం చేయగలను?',
      error: 'ఏదో తప్పు జరిగింది. దయచేసి మళ్ళీ ప్రయత్నించండి.'
    },
    // Cases
    cases: {
      title: 'నా కేసులు',
      newCase: 'కొత్త కేసు',
      allCases: 'అన్ని కేసులు',
      active: 'సక్రియం',
      pending: 'పెండింగ్',
      resolved: 'పరిష్కరించబడింది',
      closed: 'మూసివేయబడింది',
      draft: 'డ్రాఫ్ట్',
      search: 'కేసులను వెతకండి...',
      noResults: 'కేసులు కనుగొనబడలేదు',
      createCase: 'కొత్త కేసు సృష్టించండి',
      caseTitle: 'కేసు శీర్షిక',
      description: 'వివరణ',
      status: 'స్థితి',
      priority: 'ప్రాధాన్యత',
      high: 'అధిక',
      medium: 'మధ్యస్థ',
      low: 'తక్కువ',
      documents: 'పత్రాలు',
      timeline: 'టైమ్‌లైన్',
      overview: 'అవలోకనం',
      uploadDoc: 'డాక్యుమెంట్ అప్‌లోడ్ చేయండి',
      exportPdf: 'PDF ఎగుమతి చేయండి',
      addEvent: 'ఈవెంట్ జోడించండి',
      created: 'సృష్టించబడింది',
      updated: 'నవీకరించబడింది'
    },
    // Common
    common: {
      save: 'సేవ్ చేయండి',
      cancel: 'రద్దు చేయండి',
      delete: 'తొలగించండి',
      edit: 'సవరించండి',
      view: 'చూడండి',
      download: 'డౌన్‌లోడ్',
      upload: 'అప్‌లోడ్',
      loading: 'లోడ్ అవుతోంది...',
      success: 'విజయం!',
      error: 'లోపం',
      confirm: 'నిర్ధారించండి',
      back: 'వెనక్కి',
      next: 'తదుపరి',
      submit: 'సమర్పించండి',
      close: 'మూసివేయి'
    },
    // Footer
    footer: {
      rights: 'అన్ని హక్కులు రిజర్వ్ చేయబడ్డాయి',
      privacy: 'గోప్యతా విధానం',
      terms: 'సేవా నిబంధనలు',
      madeWith: 'భారతదేశంలో ❤️ తో తయారు చేయబడింది'
    }
  }
};

export type TranslationKey = keyof typeof translations.en;
export type Translations = typeof translations.en;
