from transformers import AutoTokenizer, AutoModelForCausalLM
import torch

# Replace with the exact model name you downloaded
model_id = "meta-llama/Llama-3.1-8B"

tokenizer = AutoTokenizer.from_pretrained(model_id)

model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
    device_map="auto",  # puts it on GPU if available, CPU otherwise
)

# Prompt the model
inputs = tokenizer("Hello! How are you today?", return_tensors="pt").to(model.device)
outputs = model.generate(**inputs, max_new_tokens=50)

print(tokenizer.decode(outputs[0], skip_special_tokens=True))
