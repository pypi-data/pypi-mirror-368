"""
Sample from a trained model
"""
import os
import pickle
from contextlib import nullcontext
import torch
import pickle
import os
from microgpt.model import MicroGPTConfig, MicroGPT

# -----------------------------------------------------------------------------
# Default sampling configuration
out_dir = 'out' # directory containing the checkpoint
start = "\n" # or "<|endoftext|>" or etc. Can also specify a file, use as: "FILE:prompt.txt"
num_samples = 2 # number of samples to draw
max_new_tokens = 500 # number of tokens generated in each sample
temperature = 0.8 # 1.0 = no change, < 1.0 = less random, > 1.0 = more random, in predictions
top_k = 200 # retain only the top_k most likely tokens, clamp others to have 0 probability
seed = 1337
device = 'cuda' # examples: 'cpu', 'cuda', 'cuda:0', 'cuda:1', etc.
dtype = 'bfloat16' if torch.cuda.is_available() and torch.cuda.is_bf16_supported() else 'float16' # 'float32' or 'bfloat16' or 'float16'
compile = True # use PyTorch 2.0 to compile the model to be faster

# Load configuration from pretrain/config.py to override defaults
config_path = os.path.join(os.path.dirname(__file__), 'pretrain', 'config.py')
if os.path.exists(config_path):
    exec(open(config_path).read())
    print(f"Loaded configuration from: {config_path}")
    print(f"Using out_dir: {out_dir}")
else:
    print(f"Warning: Config file not found at {config_path}, using defaults")
# -----------------------------------------------------------------------------

torch.manual_seed(seed)
torch.cuda.manual_seed(seed)
torch.backends.cuda.matmul.allow_tf32 = True # allow tf32 on matmul
torch.backends.cudnn.allow_tf32 = True # allow tf32 on cudnn
device_type = 'cuda' if 'cuda' in device else 'cpu' # for later use in torch.autocast
ptdtype = {'float32': torch.float32, 'bfloat16': torch.bfloat16, 'float16': torch.float16}[dtype]
ctx = nullcontext() if device_type == 'cpu' else torch.amp.autocast(device_type=device_type, dtype=ptdtype)

# model - always load from checkpoint
ckpt_path = os.path.join(out_dir, 'ckpt.pt')
print(f"Loading checkpoint from: {ckpt_path}")
if not os.path.exists(ckpt_path):
    print(f"Error: Checkpoint not found at {ckpt_path}")
    print(f"Make sure you have trained a model first, or check the 'out_dir' in your config")
    exit(1)
checkpoint = torch.load(ckpt_path, map_location=device, weights_only=True)
gptconf = MicroGPTConfig(**checkpoint['model_args'])
model = MicroGPT(gptconf)
state_dict = checkpoint['model']
unwanted_prefix = '_orig_mod.'
for k,v in list(state_dict.items()):
    if k.startswith(unwanted_prefix):
        state_dict[k[len(unwanted_prefix):]] = state_dict.pop(k)
model.load_state_dict(state_dict)

model.eval()
model.to(device)
if compile:
    model = torch.compile(model) # requires PyTorch 2.0 (optional)
from hiq.vis import print_model
print_model(model)

# Try to use the data directory's meta.pkl first, then fall back to package's meta.pkl
load_meta = False
meta_path = None

# First try to find meta.pkl in the data directory (highest priority)
if 'config' in checkpoint and 'dataset' in checkpoint['config']:
    data_meta_path = os.path.join('data', checkpoint['config']['dataset'], 'meta.pkl')
    if os.path.exists(data_meta_path):
        meta_path = data_meta_path
        load_meta = True
        print(f"Using data directory meta.pkl from: {meta_path}")

# If not found in data directory, try the package's meta.pkl as fallback
if not load_meta:
    try:
        import microgpt
        package_meta_path = os.path.join(os.path.dirname(microgpt.__file__), 'meta.pkl')
        if os.path.exists(package_meta_path):
            meta_path = package_meta_path
            load_meta = True
            print(f"Using package meta.pkl from: {meta_path}")
    except ImportError:
        pass

if load_meta:
    print(f"Loading meta from {meta_path}...")
    with open(meta_path, 'rb') as f:
        meta = pickle.load(f)
    # TODO want to make this more general to arbitrary encoder/decoder schemes
    stoi, itos = meta['stoi'], meta['itos']
    encode = lambda s: [stoi[c] for c in s]
    decode = lambda l: ''.join([itos[i] for i in l])
else:
    # No meta.pkl found - this is required for character-level generation
    print("Error: No meta.pkl found. This file is required for character-level text generation.")
    print("Please ensure meta.pkl is available in the data directory or package.")
    exit(1)

# encode the beginning of the prompt
if start.startswith('FILE:'):
    with open(start[5:], 'r', encoding='utf-8') as f:
        start = f.read()
start_ids = encode(start)
x = (torch.tensor(start_ids, dtype=torch.long, device=device)[None, ...])

# run generation
with torch.no_grad():
    with ctx:
        for k in range(num_samples):
            y = model.generate(x, max_new_tokens, temperature=temperature, top_k=top_k)
            print(decode(y[0].tolist()))
            print('---------------')
