from functions import *

class Paragraph:
    def __init__(self, text: str, article_id: int, index: int):
        self.text = text
        self.article_id = article_id
        self.index = index

    def __str__(self):
        return self.text
    
    def evaluate_paragraph(self, model, tokenizer):
        return evaluate_text(self.text, model, tokenizer)
    
class Article:
    def __init__(self, article_id: int, html: str):
        self.article_id = article_id
        self.html = html
        self.paragraphs = get_article_text(self.html) or ''
        logger.info(f'\nParagraphs read: {len(self.paragraphs)}')

        self.article_length = 0
        for i, paragraph in enumerate(self.paragraphs):
            self.article_length += len(paragraph.split(' '))
            self.paragraphs[i] = Paragraph(paragraph, self.article_id, i)

        logger.info(f'First paragraph: {self.paragraphs[0].text}')
        logger.info(f'Last paragraph: {self.paragraphs[-1].text}')

    def __str__(self):
        return str(self.article_id)
    
    def evaluate_article(self, model, tokenizer):
        scores = []
        for paragraph in self.paragraphs:
            paragraph_score = paragraph.evaluate_paragraph(model, tokenizer)
            weighted_score = paragraph_score * len(paragraph.text.split(' '))
            scores.append(weighted_score)

        weighted_average = sum(scores) / self.article_length

        if self.article_length == 0:
            return 0.0
        else:
            return weighted_average