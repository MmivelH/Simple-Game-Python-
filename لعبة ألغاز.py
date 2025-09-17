import requests
import random
import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext, Toplevel

class AIChatWindow:
    def __init__(self, parent, api_key):
        self.parent = parent
        self.api_key = api_key
        
        # Create the chat window
        self.window = Toplevel(parent)
        self.window.title("المحادثة مع الذكاء الاصطناعي")
        self.window.geometry("600x500")
        
        # Chat history text area
        self.chat_history = scrolledtext.ScrolledText(
            self.window, 
            wrap=tk.WORD, 
            width=70, 
            height=20, 
            font=("Arial", 12)
        )
        self.chat_history.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.chat_history.config(state=tk.DISABLED)
        
        # User input area
        self.input_frame = ttk.Frame(self.window)
        self.input_frame.pack(padx=10, pady=5, fill=tk.X)
        
        self.user_input = ttk.Entry(self.input_frame, font=("Arial", 12), width=50)
        self.user_input.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        
        # Send button
        send_button = ttk.Button(self.input_frame, text="إرسال", command=self.send_message)
        send_button.pack(side=tk.RIGHT)
        
        # Bind Enter key to send message
        self.user_input.bind("<Return>", lambda event: self.send_message())
        
        # Initialize conversation context
        self.conversation_history = []
        
        # Add welcome message
        self.add_message("مساعد", "مرحباً! كيف يمكنني مساعدتك اليوم؟")

    def send_message(self):
        # Get user input
        user_message = self.user_input.get().strip()
        if not user_message:
            return
        
        # Clear input field
        self.user_input.delete(0, tk.END)
        
        # Display user message
        self.add_message("أنت", user_message)
        
        try:
            # Prepare request to DeepSeek API
            url = "https://api.deepseek.com/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            # Prepare messages
            messages = [{"role": "system", "content": "أنت مساعد ذكي ومفيد"}]
            messages.extend([
                {"role": "user" if msg["role"] == "أنت" else "assistant", "content": msg["text"]} 
                for msg in self.conversation_history
            ])
            messages.append({"role": "user", "content": user_message})
            
            # Request payload
            payload = {
                "model": "deepseek-chat",
                "messages": messages,
                "temperature": 0.7,
                "top_p": 1,
                "stream": False
            }
            
            # Send request
            response = requests.post(url, headers=headers, json=payload)
            
            # Check response
            if response.status_code == 200:
                # Parse response
                result = response.json()
                ai_response = result['choices'][0]['message']['content']
                
                # Display AI response
                self.add_message("مساعد", ai_response)
            else:
                # Handle error
                error_message = f"خطأ في الاتصال: {response.text}"
                self.add_message("خطأ", error_message)
            
        except Exception as e:
            error_message = f"حدث خطأ: {str(e)}"
            self.add_message("خطأ", error_message)

    def add_message(self, sender, message):
        # Enable text widget for editing
        self.chat_history.config(state=tk.NORMAL)
        
        # Add message to history
        self.chat_history.insert(tk.END, f"{sender}: {message}\n\n")
        
        # Add to conversation context
        self.conversation_history.append({"role": sender, "text": message})
        
        # Trim conversation history if it gets too long
        if len(self.conversation_history) > 10:
            self.conversation_history.pop(0)
        
        # Scroll to the end
        self.chat_history.see(tk.END)
        
        # Disable editing
        self.chat_history.config(state=tk.DISABLED)

class RiddleGameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("لعبة الألغاز")
        self.root.geometry("600x400")
        
        self.api_key = "your_deepseek_api_key_here"
        self.riddles = [
            {"question": "ما هو الشيء الذي يمشي بلا أرجل؟", "answer": "الساعة"},
            {"question": "ما هو الشيء الذي كلما أخذت منه كبر؟", "answer": "الحفرة"},
            {"question": "له أسنان ولا يعض، ما هو؟", "answer": "المشط"},    
        ]
        self.current_riddle = None
        
        self.setup_ui()
        self.create_context_menu()

    def setup_ui(self):
        ttk.Label(self.root, text="🎯 لعبة الألغاز", font=("Arial", 18, "bold")).pack(pady=10)
        
        self.question_label = ttk.Label(self.root, text="اضغط على 'لغز جديد' لبدء اللعب", font=("Arial", 14))
        self.question_label.pack(pady=20)
        
        self.answer_entry = ttk.Entry(self.root, font=("Arial", 14))
        self.answer_entry.pack(pady=10)
        
        ttk.Button(self.root, text="✅ تحقق من الإجابة", command=self.check_answer).pack(pady=5)
        ttk.Button(self.root, text="⏭️ لغز جديد", command=self.next_riddle).pack(pady=5)
        ttk.Button(self.root, text="💬 محادثة الذكاء الاصطناعي", command=self.open_ai_chat).pack(pady=5)
        ttk.Button(self.root, text="❌ خروج", command=self.root.quit).pack(pady=10)
        
        self.next_riddle()

    def open_ai_chat(self):
        # Open a new window for AI chat
        AIChatWindow(self.root, self.api_key)

    def create_context_menu(self):
        # Create a context menu for copy-paste functionality
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="نسخ", command=self.copy)
        self.context_menu.add_command(label="لصق", command=self.paste)
        self.context_menu.add_command(label="قص", command=self.cut)

        # Bind right-click to show context menu
        self.answer_entry.bind("<Button-3>", self.show_context_menu)
        
        # Add keyboard shortcuts
        self.root.bind("<Control-c>", lambda e: self.copy())
        self.root.bind("<Control-v>", lambda e: self.paste())
        self.root.bind("<Control-x>", lambda e: self.cut())

    def show_context_menu(self, event):
        # Show context menu at the cursor position
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def copy(self):
        # Copy selected text or entire text to clipboard
        try:
            selected_text = self.answer_entry.selection_get()
        except tk.TclError:
            selected_text = self.answer_entry.get()
        
        self.root.clipboard_clear()
        self.root.clipboard_append(selected_text)

    def paste(self):
        # Paste text from clipboard
        try:
            clipboard_text = self.root.clipboard_get()
            self.answer_entry.delete(0, tk.END)
            self.answer_entry.insert(0, clipboard_text)
        except tk.TclError:
            messagebox.showwarning("خطأ", "لا يوجد نص في الحافظة")

    def cut(self):
        # Cut selected text
        try:
            selected_text = self.answer_entry.selection_get()
            self.root.clipboard_clear()
            self.root.clipboard_append(selected_text)
            self.answer_entry.delete(self.answer_entry.index(tk.ANCHOR), tk.END)
        except tk.TclError:
            messagebox.showwarning("خطأ", "لم يتم تحديد أي نص")

    def check_answer(self):
        user_answer = self.answer_entry.get().strip().lower()
        if self.current_riddle and user_answer == self.current_riddle["answer"].lower():
            messagebox.showinfo("إجابة صحيحة!", "🎉 أحسنت! إجابتك صحيحة.")
        else:
            messagebox.showwarning("إجابة خاطئة", f"❌ الإجابة الصحيحة هي: {self.current_riddle['answer']}")
        self.answer_entry.delete(0, tk.END)

    def next_riddle(self):
        self.current_riddle = random.choice(self.riddles)
        self.question_label.config(text=self.current_riddle["question"])
        self.answer_entry.delete(0, tk.END)
        
if __name__ == "__main__":
    root = tk.Tk()
    app = RiddleGameApp(root)

    root.mainloop()
