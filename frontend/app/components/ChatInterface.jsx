'use client';

import { useState, useRef, useEffect } from 'react';
import { PaperAirplaneIcon, SparklesIcon, GlobeAltIcon } from '@heroicons/react/24/solid';
import { UserCircleIcon } from '@heroicons/react/24/outline';
import { chatAPI } from '../services/api';

const chatTranslations = {
  'en-US': {
    greeting: "Hello! I'm TravelGenie, your AI travel assistant. I can help you plan your perfect trip. Where would you like to go?",
    assistant: 'AI Travel Assistant',
    placeholder: 'Ask me anything about travel...',
    quickSuggestionsLabel: 'Quick suggestions:',
    quickSuggestions: {
      initial: [
        'Plan a trip to Paris',
        'Best beaches in the world',
        'Budget travel tips',
        'Adventure destinations',
      ],
      destinations: [
        'Create a 5-day itinerary',
        'Best local restaurants',
        'Hidden gems to explore',
        'Where to stay',
      ],
      planning: [
        'What to pack',
        'Visa requirements',
        'Best time to visit',
        'Local transportation',
      ],
      activities: [
        'Top attractions nearby',
        'Day trip ideas',
        'Nightlife spots',
        'Cultural experiences',
      ],
      food: [
        'Must-try local dishes',
        'Street food recommendations',
        'Fine dining options',
        'Food tours available',
      ],
      budget: [
        'Save money on flights',
        'Affordable accommodations',
        'Free activities',
        'Budget breakdown',
      ],
    },
    responses: {
      greetings: [
        "I'd be happy to help you plan an amazing trip! What type of experience are you looking for - adventure, relaxation, culture, or nature?",
        'Great! Tell me about your travel preferences. Do you prefer beaches, mountains, cities, or cultural destinations?',
      ],
      destinations: [
        'Excellent choice! For that destination, I recommend staying 5-7 days. Would you like me to suggest some must-visit attractions and local experiences?',
        "That sounds wonderful! I can help you create a detailed itinerary. What's your budget range and travel dates?",
      ],
      budget: [
        'Based on your budget, I can suggest accommodations, activities, and dining options. Would you like me to create a day-by-day itinerary?',
        "Perfect! I'll factor that into the recommendations. Are you traveling solo, with family, or with friends?",
      ],
      default: [
        'I understand. Let me help you with that. Could you provide more details so I can give you the best recommendations?',
        "That's interesting! Tell me more about what you're looking for, and I'll create personalized suggestions for you.",
      ],
    },
  },
  'es-ES': {
    greeting: '¡Hola! Soy TravelGenie, tu asistente de viajes con IA. Puedo ayudarte a planificar tu viaje perfecto. ¿A dónde te gustaría ir?',
    assistant: 'Asistente de Viajes IA',
    placeholder: 'Pregúntame cualquier cosa sobre viajes...',
    quickSuggestionsLabel: 'Sugerencias rápidas:',
    quickSuggestions: {
      initial: [
        'Planificar viaje a París',
        'Mejores playas del mundo',
        'Consejos de viaje económico',
        'Destinos de aventura',
      ],
      destinations: [
        'Crear itinerario de 5 días',
        'Mejores restaurantes locales',
        'Lugares secretos para explorar',
        'Dónde alojarse',
      ],
      planning: [
        'Qué empacar',
        'Requisitos de visa',
        'Mejor época para visitar',
        'Transporte local',
      ],
      activities: [
        'Principales atracciones',
        'Ideas de excursiones',
        'Vida nocturna',
        'Experiencias culturales',
      ],
      food: [
        'Platos típicos locales',
        'Comida callejera',
        'Opciones gourmet',
        'Tours gastronómicos',
      ],
      budget: [
        'Ahorrar en vuelos',
        'Alojamiento económico',
        'Actividades gratuitas',
        'Desglose de presupuesto',
      ],
    },
    responses: {
      greetings: [
        '¡Estaré encantado de ayudarte a planificar un viaje increíble! ¿Qué tipo de experiencia buscas: aventura, relajación, cultura o naturaleza?',
        '¡Genial! Cuéntame sobre tus preferencias de viaje. ¿Prefieres playas, montañas, ciudades o destinos culturales?',
      ],
      destinations: [
        '¡Excelente elección! Para ese destino, recomiendo quedarse 5-7 días. ¿Te gustaría que sugiera atracciones imperdibles y experiencias locales?',
        '¡Eso suena maravilloso! Puedo ayudarte a crear un itinerario detallado. ¿Cuál es tu rango de presupuesto y fechas de viaje?',
      ],
      budget: [
        'Según tu presupuesto, puedo sugerir alojamientos, actividades y opciones gastronómicas. ¿Te gustaría que cree un itinerario día a día?',
        '¡Perfecto! Lo tendré en cuenta para las recomendaciones. ¿Viajas solo, con familia o con amigos?',
      ],
      default: [
        'Entiendo. Déjame ayudarte con eso. ¿Podrías proporcionar más detalles para darte las mejores recomendaciones?',
        '¡Interesante! Cuéntame más sobre lo que buscas y crearé sugerencias personalizadas para ti.',
      ],
    },
  },
  'fr-FR': {
    greeting: "Bonjour! Je suis TravelGenie, votre assistant de voyage IA. Je peux vous aider à planifier votre voyage parfait. Où aimeriez-vous aller?",
    assistant: 'Assistant de Voyage IA',
    placeholder: 'Posez-moi n\'importe quelle question sur les voyages...',
    quickSuggestionsLabel: 'Suggestions rapides:',
    quickSuggestions: {
      initial: ['Voyage à Paris', 'Meilleures plages', 'Voyager petit budget', 'Destinations aventure'],
      destinations: ['Itinéraire 5 jours', 'Restaurants locaux', 'Lieux secrets', 'Où séjourner'],
      planning: ['Quoi emporter', 'Visa requis', 'Meilleure période', 'Transport local'],
      activities: ['Attractions top', 'Excursions', 'Vie nocturne', 'Expériences culturelles'],
      food: ['Plats locaux', 'Street food', 'Gastronomie', 'Tours culinaires'],
      budget: ['Économiser sur vols', 'Hébergement abordable', 'Activités gratuites', 'Budget détaillé'],
    },
    responses: {
      greetings: [
        "Je serais ravi de vous aider à planifier un voyage incroyable! Quel type d'expérience recherchez-vous: aventure, détente, culture ou nature?",
        "Super! Parlez-moi de vos préférences de voyage. Préférez-vous les plages, les montagnes, les villes ou les destinations culturelles?",
      ],
      destinations: [
        "Excellent choix! Pour cette destination, je recommande de rester 5-7 jours. Voulez-vous que je suggère des attractions incontournables et des expériences locales?",
        "Ça a l'air merveilleux! Je peux vous aider à créer un itinéraire détaillé. Quel est votre budget et vos dates de voyage?",
      ],
      budget: [
        "Selon votre budget, je peux suggérer des hébergements, activités et options de restauration. Voulez-vous que je crée un itinéraire jour par jour?",
        "Parfait! Je prendrai cela en compte pour les recommandations. Voyagez-vous seul, en famille ou entre amis?",
      ],
      default: [
        "Je comprends. Laissez-moi vous aider. Pourriez-vous fournir plus de détails pour que je puisse vous donner les meilleures recommandations?",
        "C'est intéressant! Dites-m'en plus sur ce que vous recherchez et je créerai des suggestions personnalisées pour vous.",
      ],
    },
  },
  'de-DE': {
    greeting: "Hallo! Ich bin TravelGenie, Ihr KI-Reiseassistent. Ich kann Ihnen helfen, Ihre perfekte Reise zu planen. Wohin möchten Sie reisen?",
    assistant: 'KI-Reiseassistent',
    placeholder: 'Fragen Sie mich alles über Reisen...',
    quickSuggestionsLabel: 'Schnelle Vorschläge:',
    quickSuggestions: {
      initial: ['Reise nach Paris', 'Beste Strände', 'Budget-Reisetipps', 'Abenteuer-Ziele'],
      destinations: ['5-Tage-Reiseplan', 'Lokale Restaurants', 'Geheimtipps', 'Unterkünfte'],
      planning: ['Packliste', 'Visum-Infos', 'Beste Reisezeit', 'Nahverkehr'],
      activities: ['Top Sehenswürdigkeiten', 'Tagesausflüge', 'Nachtleben', 'Kultur erleben'],
      food: ['Lokale Küche', 'Street Food', 'Fine Dining', 'Food-Touren'],
      budget: ['Flüge sparen', 'Günstige Hotels', 'Kostenlose Aktivitäten', 'Kostenübersicht'],
    },
    responses: {
      greetings: [
        'Ich helfe Ihnen gerne bei der Planung einer fantastischen Reise! Welche Art von Erlebnis suchen Sie - Abenteuer, Entspannung, Kultur oder Natur?',
        'Toll! Erzählen Sie mir von Ihren Reisepräferenzen. Bevorzugen Sie Strände, Berge, Städte oder kulturelle Ziele?',
      ],
      destinations: [
        'Ausgezeichnete Wahl! Für dieses Reiseziel empfehle ich 5-7 Tage. Möchten Sie, dass ich Must-See-Attraktionen und lokale Erlebnisse vorschlage?',
        'Das klingt wunderbar! Ich kann Ihnen helfen, einen detaillierten Reiseplan zu erstellen. Was ist Ihr Budget und Ihre Reisedaten?',
      ],
      budget: [
        'Basierend auf Ihrem Budget kann ich Unterkünfte, Aktivitäten und Restaurants vorschlagen. Möchten Sie einen Tag-für-Tag-Reiseplan?',
        'Perfekt! Das werde ich bei den Empfehlungen berücksichtigen. Reisen Sie allein, mit Familie oder mit Freunden?',
      ],
      default: [
        'Verstehe. Lassen Sie mich Ihnen dabei helfen. Könnten Sie weitere Details angeben, damit ich die besten Empfehlungen geben kann?',
        'Interessant! Erzählen Sie mir mehr darüber, was Sie suchen, und ich erstelle personalisierte Vorschläge für Sie.',
      ],
    },
  },
  'ja-JP': {
    greeting: "こんにちは！私はTravelGenie、あなたのAI旅行アシスタントです。完璧な旅行の計画をお手伝いします。どこに行きたいですか？",
    assistant: 'AI旅行アシスタント',
    placeholder: '旅行について何でも聞いてください...',
    quickSuggestionsLabel: 'クイック提案:',
    quickSuggestions: {
      initial: ['パリ旅行を計画', '最高のビーチ', '格安旅行のコツ', '冒険の目的地'],
      destinations: ['5日間の旅程', '地元のレストラン', '隠れた名所', '宿泊先'],
      planning: ['持ち物リスト', 'ビザ情報', 'ベストシーズン', '交通機関'],
      activities: ['人気スポット', '日帰り旅行', 'ナイトライフ', '文化体験'],
      food: ['地元料理', '屋台グルメ', '高級レストラン', 'フードツアー'],
      budget: ['航空券を節約', '格安宿泊', '無料アクティビティ', '予算内訳'],
    },
    responses: {
      greetings: [
        '素晴らしい旅行の計画をお手伝いします！どんな体験をお探しですか - 冒険、リラクゼーション、文化、それとも自然？',
        '素晴らしい！旅行の好みを教えてください。ビーチ、山、都市、文化的な目的地、どれがお好みですか？',
      ],
      destinations: [
        '素晴らしい選択です！その目的地には5〜7日間の滞在をお勧めします。必見のアトラクションやローカル体験を提案しましょうか？',
        '素敵ですね！詳細な旅程を作成するお手伝いができます。予算と旅行日程を教えてください。',
      ],
      budget: [
        'ご予算に基づいて、宿泊施設、アクティビティ、食事のオプションを提案できます。日別の旅程を作成しましょうか？',
        '完璧です！それを考慮して提案します。一人旅ですか、家族と一緒ですか、それとも友人とですか？',
      ],
      default: [
        'わかりました。お手伝いします。最適な提案ができるよう、もう少し詳しく教えていただけますか？',
        '興味深いですね！お探しのものについてもっと教えてください。パーソナライズされた提案を作成します。',
      ],
    },
  },
  'zh-CN': {
    greeting: "您好！我是TravelGenie，您的AI旅行助手。我可以帮您规划完美的旅程。您想去哪里？",
    assistant: 'AI旅行助手',
    placeholder: '问我任何关于旅行的问题...',
    quickSuggestionsLabel: '快速建议:',
    quickSuggestions: {
      initial: ['巴黎之旅', '最美海滩', '省钱攻略', '冒险目的地'],
      destinations: ['5天行程', '当地美食', '小众景点', '住宿推荐'],
      planning: ['打包清单', '签证信息', '最佳时间', '当地交通'],
      activities: ['热门景点', '一日游', '夜生活', '文化体验'],
      food: ['必吃美食', '街边小吃', '高档餐厅', '美食之旅'],
      budget: ['机票省钱', '平价住宿', '免费活动', '预算明细'],
    },
    responses: {
      greetings: [
        '我很乐意帮您规划一次精彩的旅行！您在寻找什么类型的体验 - 冒险、休闲、文化还是自然？',
        '太好了！告诉我您的旅行偏好。您更喜欢海滩、山脉、城市还是文化目的地？',
      ],
      destinations: [
        '很棒的选择！对于这个目的地，我建议停留5-7天。您想让我推荐一些必游景点和当地体验吗？',
        '听起来很棒！我可以帮您创建详细的行程。您的预算范围和旅行日期是什么？',
      ],
      budget: [
        '根据您的预算，我可以推荐住宿、活动和餐饮选择。您想让我创建一个逐日行程吗？',
        '完美！我会将此纳入推荐考虑。您是独自旅行、与家人还是与朋友一起？',
      ],
      default: [
        '我理解。让我来帮助您。您能提供更多细节以便我给出最佳建议吗？',
        '很有趣！告诉我更多关于您正在寻找的内容，我会为您创建个性化建议。',
      ],
    },
  },
  'pt-BR': {
    greeting: "Olá! Sou o TravelGenie, seu assistente de viagem com IA. Posso ajudá-lo a planejar sua viagem perfeita. Para onde você gostaria de ir?",
    assistant: 'Assistente de Viagem IA',
    placeholder: 'Pergunte-me qualquer coisa sobre viagens...',
    quickSuggestionsLabel: 'Sugestões rápidas:',
    quickSuggestions: {
      initial: ['Viagem para Paris', 'Melhores praias', 'Dicas econômicas', 'Destinos de aventura'],
      destinations: ['Roteiro de 5 dias', 'Restaurantes locais', 'Lugares secretos', 'Onde ficar'],
      planning: ['O que levar', 'Requisitos de visto', 'Melhor época', 'Transporte local'],
      activities: ['Principais atrações', 'Passeios de um dia', 'Vida noturna', 'Experiências culturais'],
      food: ['Comidas típicas', 'Comida de rua', 'Restaurantes finos', 'Tours gastronômicos'],
      budget: ['Economizar em voos', 'Hospedagem barata', 'Atividades gratuitas', 'Detalhes do orçamento'],
    },
    responses: {
      greetings: [
        'Ficarei feliz em ajudá-lo a planejar uma viagem incrível! Que tipo de experiência você está procurando - aventura, relaxamento, cultura ou natureza?',
        'Ótimo! Conte-me sobre suas preferências de viagem. Você prefere praias, montanhas, cidades ou destinos culturais?',
      ],
      destinations: [
        'Excelente escolha! Para esse destino, recomendo ficar 5-7 dias. Gostaria que eu sugerisse atrações imperdíveis e experiências locais?',
        'Isso parece maravilhoso! Posso ajudá-lo a criar um roteiro detalhado. Qual é sua faixa de orçamento e datas de viagem?',
      ],
      budget: [
        'Com base no seu orçamento, posso sugerir acomodações, atividades e opções gastronômicas. Gostaria que eu criasse um roteiro dia a dia?',
        'Perfeito! Vou levar isso em consideração nas recomendações. Você está viajando sozinho, com família ou com amigos?',
      ],
      default: [
        'Entendo. Deixe-me ajudá-lo com isso. Você poderia fornecer mais detalhes para que eu possa dar as melhores recomendações?',
        'Interessante! Conte-me mais sobre o que você está procurando e criarei sugestões personalizadas para você.',
      ],
    },
  },
  'hi-IN': {
    greeting: "नमस्ते! मैं TravelGenie हूं, आपका AI यात्रा सहायक। मैं आपकी परफेक्ट यात्रा की योजना बनाने में मदद कर सकता हूं। आप कहां जाना चाहेंगे?",
    assistant: 'AI यात्रा सहायक',
    placeholder: 'यात्रा के बारे में कुछ भी पूछें...',
    quickSuggestionsLabel: 'त्वरित सुझाव:',
    quickSuggestions: {
      initial: ['पेरिस यात्रा', 'सर्वश्रेष्ठ समुद्र तट', 'बजट यात्रा टिप्स', 'साहसिक स्थल'],
      destinations: ['5 दिन का प्लान', 'स्थानीय रेस्तरां', 'छिपे हुए स्थान', 'कहां रुकें'],
      planning: ['क्या पैक करें', 'वीज़ा जानकारी', 'जाने का सबसे अच्छा समय', 'स्थानीय परिवहन'],
      activities: ['टॉप आकर्षण', 'दिन की यात्राएं', 'नाइटलाइफ', 'सांस्कृतिक अनुभव'],
      food: ['स्थानीय व्यंजन', 'स्ट्रीट फूड', 'फाइन डाइनिंग', 'फूड टूर'],
      budget: ['फ्लाइट बचत', 'सस्ता आवास', 'मुफ्त गतिविधियां', 'बजट विवरण'],
    },
    responses: {
      greetings: [
        'मुझे एक अद्भुत यात्रा की योजना बनाने में आपकी मदद करने में खुशी होगी! आप किस प्रकार का अनुभव चाहते हैं - साहसिक, विश्राम, संस्कृति, या प्रकृति?',
        'बढ़िया! मुझे अपनी यात्रा प्राथमिकताओं के बारे में बताएं। आप समुद्र तट, पहाड़, शहर, या सांस्कृतिक गंतव्य पसंद करते हैं?',
      ],
      destinations: [
        'उत्कृष्ट विकल्प! उस गंतव्य के लिए, मैं 5-7 दिन रहने की सिफारिश करता हूं। क्या आप चाहते हैं कि मैं कुछ अवश्य देखने योग्य आकर्षण और स्थानीय अनुभव सुझाऊं?',
        'यह अद्भुत लगता है! मैं आपको एक विस्तृत यात्रा कार्यक्रम बनाने में मदद कर सकता हूं। आपका बजट और यात्रा तिथियां क्या हैं?',
      ],
      budget: [
        'आपके बजट के आधार पर, मैं आवास, गतिविधियां और भोजन विकल्प सुझा सकता हूं। क्या आप चाहते हैं कि मैं एक दिन-प्रतिदिन यात्रा कार्यक्रम बनाऊं?',
        'बिल्कुल सही! मैं इसे सिफारिशों में शामिल करूंगा। आप अकेले यात्रा कर रहे हैं, परिवार के साथ, या दोस्तों के साथ?',
      ],
      default: [
        'मैं समझता हूं। मुझे इसमें आपकी मदद करने दें। क्या आप अधिक विवरण दे सकते हैं ताकि मैं सबसे अच्छी सिफारिशें दे सकूं?',
        'दिलचस्प! मुझे और बताएं कि आप क्या खोज रहे हैं, और मैं आपके लिए व्यक्तिगत सुझाव बनाऊंगा।',
      ],
    },
  },
  'ar-SA': {
    greeting: "مرحباً! أنا TravelGenie، مساعد السفر الذكي الخاص بك. يمكنني مساعدتك في التخطيط لرحلتك المثالية. إلى أين تريد الذهاب؟",
    assistant: 'مساعد السفر الذكي',
    placeholder: 'اسألني أي شيء عن السفر...',
    quickSuggestionsLabel: 'اقتراحات سريعة:',
    quickSuggestions: {
      initial: ['رحلة إلى باريس', 'أفضل الشواطئ', 'نصائح السفر الاقتصادي', 'وجهات المغامرة'],
      destinations: ['خطة 5 أيام', 'مطاعم محلية', 'أماكن مخفية', 'أين تقيم'],
      planning: ['ماذا تحزم', 'معلومات التأشيرة', 'أفضل وقت للزيارة', 'النقل المحلي'],
      activities: ['أهم المعالم', 'رحلات يومية', 'الحياة الليلية', 'تجارب ثقافية'],
      food: ['أطباق محلية', 'طعام الشارع', 'مطاعم فاخرة', 'جولات الطعام'],
      budget: ['توفير في الطيران', 'إقامة رخيصة', 'أنشطة مجانية', 'تفاصيل الميزانية'],
    },
    responses: {
      greetings: [
        'يسعدني مساعدتك في التخطيط لرحلة رائعة! ما نوع التجربة التي تبحث عنها - مغامرة أم استرخاء أم ثقافة أم طبيعة؟',
        'رائع! أخبرني عن تفضيلات سفرك. هل تفضل الشواطئ أم الجبال أم المدن أم الوجهات الثقافية؟',
      ],
      destinations: [
        'اختيار ممتاز! لهذه الوجهة، أوصي بالبقاء 5-7 أيام. هل تريد أن أقترح معالم سياحية لا بد من زيارتها وتجارب محلية؟',
        'يبدو رائعاً! يمكنني مساعدتك في إنشاء برنامج رحلة مفصل. ما هي ميزانيتك وتواريخ سفرك؟',
      ],
      budget: [
        'بناءً على ميزانيتك، يمكنني اقتراح أماكن إقامة وأنشطة وخيارات طعام. هل تريد أن أنشئ برنامجاً يومياً؟',
        'ممتاز! سأضع ذلك في الاعتبار عند تقديم التوصيات. هل تسافر بمفردك أم مع العائلة أم مع الأصدقاء؟',
      ],
      default: [
        'أفهم. دعني أساعدك في ذلك. هل يمكنك تقديم مزيد من التفاصيل حتى أتمكن من إعطائك أفضل التوصيات؟',
        'مثير للاهتمام! أخبرني المزيد عما تبحث عنه وسأقوم بإنشاء اقتراحات مخصصة لك.',
      ],
    },
  },
};

export default function ChatInterface({ selectedLanguage, initialPrompt = '' }) {
  const t = chatTranslations[selectedLanguage] || chatTranslations['en-US'];

  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'bot',
      content: t.greeting,
      timestamp: new Date(Date.now() - 300000),
    },
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [suggestionCategory, setSuggestionCategory] = useState('initial');
  const [lastProcessedPrompt, setLastProcessedPrompt] = useState('');
  const [isClient, setIsClient] = useState(false);
  const messagesEndRef = useRef(null);
  const messagesContainerRef = useRef(null);
  const inputRef = useRef(null);

  // Set isClient to true after component mounts (client-side only)
  useEffect(() => {
    setIsClient(true);
  }, []);

  // Handle initial prompt from AI integration
  useEffect(() => {
    if (initialPrompt && initialPrompt !== lastProcessedPrompt) {
      setLastProcessedPrompt(initialPrompt);
      setInputValue(initialPrompt);
      // Focus the input
      if (inputRef.current) {
        inputRef.current.focus();
      }
    }
  }, [initialPrompt, lastProcessedPrompt]);

  // Function to detect conversation context and update suggestions
  const detectContext = (allMessages) => {
    const recentMessages = allMessages.slice(-4).map(m => m.content.toLowerCase()).join(' ');
    
    // Keywords for different categories
    const contextKeywords = {
      food: ['food', 'eat', 'restaurant', 'cuisine', 'dish', 'meal', 'hungry', 'lunch', 'dinner', 'breakfast', 'cafe', 'comida', 'comer', 'restaurante', 'nourriture', 'manger', 'essen', 'खाना', 'レストラン', '餐厅', '食物'],
      budget: ['budget', 'cheap', 'affordable', 'money', 'cost', 'price', 'save', 'expensive', 'presupuesto', 'barato', 'économique', 'günstig', 'बजट', '予算', '预算'],
      activities: ['things to do', 'activities', 'attractions', 'visit', 'see', 'explore', 'tour', 'museum', 'park', 'actividades', 'activités', 'aktivitäten', 'गतिविधियां', 'アクティビティ', '活动'],
      planning: ['pack', 'visa', 'when to', 'best time', 'weather', 'transport', 'flight', 'hotel', 'stay', 'planificar', 'planifier', 'planen', 'योजना', '計画', '计划'],
      destinations: ['itinerary', 'days', 'trip', 'travel to', 'going to', 'visit', 'recommend', 'destination', 'viaje', 'voyage', 'reise', 'यात्रा', '旅行'],
    };
    
    // Check each category
    for (const [category, keywords] of Object.entries(contextKeywords)) {
      if (keywords.some(keyword => recentMessages.includes(keyword))) {
        return category;
      }
    }
    
    // If we have more than 2 messages, rotate through categories
    if (allMessages.length > 2) {
      const categories = ['destinations', 'activities', 'food', 'planning', 'budget'];
      return categories[Math.floor(Math.random() * categories.length)];
    }
    
    return 'initial';
  };

  // Update initial message when language changes
  useEffect(() => {
    const newT = chatTranslations[selectedLanguage] || chatTranslations['en-US'];
    setMessages([
      {
        id: 1,
        type: 'bot',
        content: newT.greeting,
        timestamp: new Date(Date.now() - 300000),
      },
    ]);
  }, [selectedLanguage]);

  const scrollToBottom = () => {
    if (messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop = messagesContainerRef.current.scrollHeight;
    }
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Function to get bot response from Gemini API
  const getBotResponse = async (userMessage) => {
    setIsTyping(true);
    
    try {
      // Build conversation history from messages (excluding the initial greeting)
      const conversationHistory = messages
        .filter(msg => msg.id !== 1)
        .map(msg => ({
          role: msg.type === 'user' ? 'user' : 'assistant',
          content: msg.content
        }));

      // Call the API with conversation history for context
      const response = await chatAPI.sendMessage(
        userMessage,
        selectedLanguage,
        conversationHistory
      );
      
      const newBotMessage = {
        id: Date.now(),
        type: 'bot',
        content: response.message,
        timestamp: new Date(response.created_at || Date.now()),
      };
      
      setMessages(prev => {
        const updated = [...prev, newBotMessage];
        // Update suggestion category based on conversation context
        setSuggestionCategory(detectContext(updated));
        return updated;
      });
    } catch (error) {
      console.error('API Error:', error);
      
      const errorMessage = error.message?.includes('API key') 
        ? 'Please configure your API key in the backend .env file.'
        : error.message || 'Sorry, I encountered an error. Please try again.';

      setMessages(prev => [
        ...prev,
        {
          id: Date.now(),
          type: 'bot',
          content: errorMessage,
          timestamp: new Date(),
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSendMessage = (e) => {
    e.preventDefault();
    
    if (!inputValue.trim()) return;

    const newMessage = {
      id: Date.now(),
      type: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages(prev => {
      const updated = [...prev, newMessage];
      // Update suggestion category when user sends message
      setSuggestionCategory(detectContext(updated));
      return updated;
    });
    const messageToSend = inputValue;
    setInputValue('');
    
    // Call the API
    getBotResponse(messageToSend);
  };

  const formatTime = (date) => {
    return new Intl.DateTimeFormat(selectedLanguage, {
      hour: '2-digit',
      minute: '2-digit',
    }).format(date);
  };
  
  // Get current suggestions based on category
  const getCurrentSuggestions = () => {
    const suggestions = currentT.quickSuggestions;
    if (typeof suggestions === 'object' && !Array.isArray(suggestions)) {
      return suggestions[suggestionCategory] || suggestions.initial || [];
    }
    // Fallback for languages that haven't been updated yet
    return Array.isArray(suggestions) ? suggestions : [];
  };

  const currentT = chatTranslations[selectedLanguage] || chatTranslations['en-US'];

  return (
    <div className="flex flex-col h-full max-h-[600px] bg-(--color-surface) rounded-2xl shadow-xl border border-(--color-border) overflow-hidden">
      {/* Chat Header */}
      <div className="flex items-center justify-between px-6 py-4 bg-gradient-to-r from-(--color-primary) to-(--color-secondary) text-white">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
            <SparklesIcon className="w-6 h-6" />
          </div>
          <div>
            <h3 className="font-semibold text-lg">TravelGenie</h3>
            <p className="text-xs text-white/80">{currentT.assistant}</p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs bg-white/20 px-3 py-1.5 rounded-full">
          <GlobeAltIcon className="w-4 h-4" />
          <span>{selectedLanguage === 'en-US' ? 'English' : selectedLanguage === 'es-ES' ? 'Español' : selectedLanguage === 'fr-FR' ? 'Français' : selectedLanguage === 'de-DE' ? 'Deutsch' : selectedLanguage === 'ja-JP' ? '日本語' : selectedLanguage === 'zh-CN' ? '中文' : 'English'}</span>
        </div>
      </div>

      {/* Messages Container */}
      <div ref={messagesContainerRef} className="flex-1 overflow-y-auto px-6 py-4 space-y-4 hide-scrollbar bg-(--color-background-secondary)">
        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex gap-3 ${message.type === 'user' ? 'flex-row-reverse' : 'flex-row'}`}
          >
            {/* Avatar */}
            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
              message.type === 'bot' 
                ? 'bg-gradient-to-br from-(--color-primary) to-(--color-secondary) text-white' 
                : 'bg-(--color-gray-200) dark:bg-(--color-dark-surface-elevated)'
            }`}>
              {message.type === 'bot' ? (
                <SparklesIcon className="w-5 h-5" />
              ) : (
                <UserCircleIcon className="w-5 h-5 text-(--color-text-secondary)" />
              )}
            </div>

            {/* Message Bubble */}
            <div className={`flex flex-col max-w-[75%] ${message.type === 'user' ? 'items-end' : 'items-start'}`}>
              <div
                className={`px-4 py-3 rounded-2xl ${
                  message.type === 'bot'
                    ? 'bg-white dark:bg-(--color-dark-surface) shadow-sm border border-(--color-border-light)'
                    : 'bg-gradient-to-r from-(--color-primary) to-(--color-primary-light) text-white'
                }`}
              >
                <div className={`text-sm leading-relaxed ${message.type === 'bot' ? 'text-(--color-text-primary)' : 'text-white'}`}>
                  {message.type === 'bot' ? (
                    <div className="whitespace-pre-wrap" dangerouslySetInnerHTML={{
                      __html: message.content
                        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                        .replace(/\n\n/g, '<br/><br/>')
                        .replace(/\n/g, '<br/>')
                        .replace(/• /g, '<span class="inline-block ml-2">•</span> ')
                    }} />
                  ) : (
                    <p>{message.content}</p>
                  )}
                </div>
              </div>
              <span className="text-xs text-(--color-text-tertiary) mt-1 px-1">
                {isClient ? formatTime(message.timestamp) : ''}
              </span>
            </div>
          </div>
        ))}

        {/* Typing Indicator */}
        {isTyping && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-gradient-to-br from-(--color-primary) to-(--color-secondary) flex items-center justify-center flex-shrink-0">
              <SparklesIcon className="w-5 h-5 text-white" />
            </div>
            <div className="bg-white dark:bg-(--color-dark-surface) px-4 py-3 rounded-2xl shadow-sm border border-(--color-border-light)">
              <div className="flex gap-1">
                <div className="w-2 h-2 bg-(--color-primary) rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                <div className="w-2 h-2 bg-(--color-primary) rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                <div className="w-2 h-2 bg-(--color-primary) rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <form onSubmit={handleSendMessage} className="px-6 py-4 border-t border-(--color-border) bg-(--color-surface)">
        <div className="flex gap-3 items-center">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            placeholder={currentT.placeholder}
            className="flex-1 px-4 py-3 bg-(--color-background-secondary) border border-(--color-border) rounded-xl text-(--color-text-primary) placeholder:text-(--color-text-tertiary) focus:outline-hidden focus:ring-2 focus:ring-(--color-primary)/20 focus:border-(--color-primary) transition-all duration-200"
          />
          <button
            type="submit"
            disabled={!inputValue.trim()}
            className="p-3 bg-gradient-to-r from-(--color-primary) to-(--color-secondary) text-white rounded-xl hover:shadow-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed active:scale-95"
          >
            <PaperAirplaneIcon className="w-5 h-5" />
          </button>
        </div>
      </form>
    </div>
  );
}