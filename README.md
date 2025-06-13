# AdaWongBLDM

---

- 对原版 [Adabldm](https://github.com/GrandpaXun242/AdaBLDM) 的个人化修改

- 主要修改包括；
  - 新增了一些对数据集进行预处理的工具；
  - 在测试阶段不使用 `generate_triple_map` 方法，而是直接使用准备好的mask文件；
  - 基本上放弃了前景处理的部分；
  - 为了适应一些新版本的pip库，对某些代码进行了修改，不影响相关功能。
  - 附带了 `environment.yaml`