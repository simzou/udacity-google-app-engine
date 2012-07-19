from handlers.base import Handler

class ROT13Page(Handler):
    
    def get(self):
        self.render('rot13.html')
		
    def post(self):
        user_text = self.request.get('text').encode('rot13')
        text_map = {'text': user_text}
        self.render('rot13.html', **text_map)
       