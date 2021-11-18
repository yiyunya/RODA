# RODA: Reverse Operation based Data Augmentation for Solving Math Word Problems
Liu Q., Guan W., Li S., Cheng F., Kawahara D. and Kurohashi S. 



This paper has been acceptted for publication in *Transactions on Audio, Speech and Language Processing.*.

We propose a novel data augmentation method that reverses the mathematical logic of math word problems to produce new high-quality math problems
and introduce new knowledge points that can benefit learning the mathematical reasoning logic. We apply the augmented data on two SOTA math word problem solving models and compare our results with a strong data augmentation baseline.

## Data

All data used for this paper could be found in /data folder. Augment.json holds all questions augmented from Math23K, which is used for 5-cross validation evaluation. PreprocessedQuestion_enumeratefiltered(split)2.json holds the augmented data for the standard split of Math23K. checkmerge.json holds the data of origin and augmented data for the training set.

All data is saved as:

```
{'id': '1', 
'origin_id': '946', 
'target_template': ['x', '=', 'temp_c', '*', '(', 'temp_b', '-', 'temp_a', ')', '/', 'temp_a'], 
'target_norm_post_template': ['x', '=', 'temp_c', 'temp_b', 'temp_a', '-', '*', 'temp_a', '/'], 
'num_list': [1.5, 4.0, 12.0], 
'text': '甲数 除以 乙数 的 商是 temp_a , 则 甲数 是 乙 的 temp_b 倍 , 原来 甲数 temp_c , 如果 甲数 增加 =？', 
'answer': 20.0}
```

## Code

### Data Augmentation

The augmented data could be obtained by the following code:

```
python preprocessEnumerate.py --data_path='./data/train23k_processed.json' --out_path='./data/PreprocessedQuestion_enumeratefilteredtrain2.json'
```

The original data used for augmentation could be found here: https://github.com/SumbeeLei/Math_EN


### Reproduction

For reproducing the 5-fold cross-validation results, please run:

```
python run_check_merge.py
```

For reproducing the train/test setting, please run:

```
python run_check_merge.py --test_dir='data/Math_23K_test.json'
```

The original data used could be found here: https://github.com/ShichaoSun/math_seq2tree

## Citation

If you find this repo useful, please cite the following paper:

```
@misc{liu2020reverse,
      title={Reverse Operation based Data Augmentation for Solving Math Word Problems}, 
      author={Qianying Liu and Wenyu Guan and Sujian Li and Fei Cheng and Daisuke Kawahara and Sadao Kurohashi},
      year={2020},
      eprint={2010.01556},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```
