import React, { useState, FC, FormEvent } from 'react';

// Define the type for a chat message
interface Message {
  text: string;
  sender: 'user' | 'bot';
}

const AIChatbot: FC = () => {
  // State to store the conversation history
  const [messages, setMessages] = useState<Message[]>([]);
  // State to store the user's input
  const [input, setInput] = useState<string>('');
  // State to show a loading indicator while fetching the response
  const [isLoading, setIsLoading] = useState<boolean>(false);
  
  // API key for the Gemini API
  const GEMINI_API_KEY: string = "YOUR_GEMINI_API_KEY";

  // Function to send the user's message and get a response from the AI
  const handleSendMessage = async (e: FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    // Add the user's message to the conversation
    const newUserMessage: Message = { text: input, sender: 'user' };
    setMessages(prevMessages => [...prevMessages, newUserMessage]);
    setInput('');
    setIsLoading(true);

    try {
      // Craft the prompt for the AI, asking it to act as a health assistant
      const prompt = `
        You are a helpful AI health assistant.
        Please provide a concise and helpful response (in Korean) to the following health question.
        Focus on providing general advice, not a medical diagnosis.

        User's question: ${input}
      `;
      
      const payload = {
        contents: [{
          parts: [{ text: prompt }]
        }],
      };
      
      // Call the Gemini API to get the AI's response
      const apiUrl = `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-preview-05-20:generateContent?key=${GEMINI_API_KEY}`;
      const response = await fetch(apiUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.statusText}`);
      }

      const result = await response.json();
      const botText = result.candidates?.[0]?.content?.parts?.[0]?.text || '답변을 생성하는 데 실패했습니다. 다시 시도해 주세요.';

      // Add the bot's response to the conversation
      const newBotMessage: Message = { text: botText, sender: 'bot' };
      setMessages(prevMessages => [...prevMessages, newBotMessage]);

    } catch (error) {
      console.error("Failed to fetch from Gemini API:", error);
      const errorMessage: Message = { text: '오류가 발생했습니다. 잠시 후 다시 시도해 주세요.', sender: 'bot' };
      setMessages(prevMessages => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-[500px] bg-gray-50 rounded-lg shadow-inner">
      {/* Chat History Display */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.length === 0 && (
          <div className="text-center text-gray-500 italic mt-10">
            궁금한 점을 자유롭게 물어보세요!
          </div>
        )}
        {messages.map((msg, index) => (
          <div key={index} className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}>
            <div className={`p-3 max-w-sm rounded-xl whitespace-pre-wrap ${
              msg.sender === 'user' 
                ? 'bg-blue-500 text-white rounded-br-none' 
                : 'bg-gray-200 text-gray-800 rounded-bl-none'
            }`}>
              {msg.text}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex justify-start">
            <div className="p-3 bg-gray-200 rounded-xl rounded-bl-none animate-pulse">
              답변 생성 중...
            </div>
          </div>
        )}
      </div>

      {/* Message Input Form */}
      <form onSubmit={handleSendMessage} className="p-4 bg-white border-t border-gray-200 flex space-x-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          className="flex-1 p-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
          placeholder="여기에 질문을 입력하세요..."
          disabled={isLoading}
        />
        <button
          type="submit"
          disabled={isLoading}
          className={`px-4 py-2 rounded-lg font-semibold transition-colors ${
            isLoading ? 'bg-gray-400 cursor-not-allowed' : 'bg-indigo-600 text-white hover:bg-indigo-700'
          }`}
        >
          전송
        </button>
      </form>
    </div>
  );
};

export default AIChatbot;
