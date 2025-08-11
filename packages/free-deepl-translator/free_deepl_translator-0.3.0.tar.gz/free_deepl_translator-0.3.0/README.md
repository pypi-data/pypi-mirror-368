\# free-deepl-translator



Unofficial free DeepL translator client for Python.  

This package lets you translate text using DeepL without requiring an API key, by mimicking the web client protocol.



you can install it with this command : pip install free-deepl-translator





\## 🚀 Exemple



import free\_deepl\_translator as deepl

deepl\_instance = deepl.Deepl()

deepl\_instance.Session() # Create an deepl Session

print("Session created")

translated\_text = deepl\_instance.Translate("Comment allez vous ?", target\_lang = "en")

if (translated\_text\["status"] == 0):

&nbsp;   print(f"Translated text : {translated\_text\['text']}")

&nbsp;   second\_translated\_text = deepl\_instance.Translate("oui je vais bien, merci...",target\_lang = "en")

&nbsp;   if (second\_translated\_text\["status"] == 0):

&nbsp;       print(f"Translated text : {second\_translated\_text\['text']}")

&nbsp;   else:

&nbsp;       print(f"Error : {second\_translated\_text\['msg']}")

else:

&nbsp;   print(f"Error : {translated\_text\['msg']}")

