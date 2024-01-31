import transformers
import numpy as np

tokenizer = transformers.BertTokenizer.from_pretrained('bert-base-uncased')
model = transformers.BertModel.from_pretrained('bert-base-uncased')

with open('../data/cutclip.txt', 'r') as file:
    dataGenerated = file.read()

with open('speechToTextCutClip.txt', 'r') as file:
    dataTest = file.read()

tokens1 = tokenizer(dataGenerated, return_tensors='pt', max_length=512, truncation=True, padding='max_length')
tokens2 = tokenizer(dataTest, return_tensors='pt', max_length=512, truncation=True, padding='max_length')

output1 = model(**tokens1)
output2 = model(**tokens2)

embedding1 = output1.last_hidden_state[:, 0, :]
embedding2 = output2.last_hidden_state[:, 0, :]

similarity = np.dot(embedding1.detach().numpy(), embedding2.detach().numpy().T) / (np.linalg.norm(embedding1.detach().numpy()) * np.linalg.norm(embedding2.detach().numpy()))

print(similarity.item())
