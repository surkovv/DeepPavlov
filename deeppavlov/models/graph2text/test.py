from triplets_preprocessor import TripletsPreprocessor
from triplets_tokenizer import TripletsTokenizer
from graph2text_bart import GraphToTextBart

prp = TripletsPreprocessor()
tok = TripletsTokenizer(tokenizer_path="JointGT/pretrain_model/jointgt_bart")
batch = [[['Belgorod', 'head of government', 'Anton Ivanov'],
          ['Anton Ivanov', 'date of birth', '2 February 1985']]]
model = GraphToTextBart(checkpoint_path='JointGT/checkpoint/jointgt_bart_webnlg', tokenizer_path="JointGT/pretrain_model/jointgt_bart")

print(model(tok(prp(batch))))

