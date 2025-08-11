# FXTensor

マルコフ・テンソルを計算するモジュールです。

## インストール

```bash
pip install fxtensor-salmon
```

## 使い方

JSON定義から`FXTensor`オブジェクトを作成する方法は以下の通りです。

```python
import numpy as np
from fxtensor import FXTensor

json_data = {
  "profile": [[2], [2]],
  "strands": [
    {"from": [0], "to": [0], "weight": 0.3},
    {"from": [0], "to": [1], "weight": 0.7},
    {"from": [1], "to": [0], "weight": 0.5},
    {"from": [1], "to": [1], "weight": 0.5}
  ]
}

# JSONデータからテンソルを作成
stochastic_map = FXTensor.from_json(json_data)

print(stochastic_map)
# 出力予測: FXTensor(profile=[[2], [2]], shape=(2, 2))

print(stochastic_map.data)
# 出力予測:
# [[0.3 0.7]
#  [0.5 0.5]]
```
