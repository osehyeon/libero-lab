# 패치 파일에 대한 고지

`libero-fixes.patch` 는 [LIBERO](https://github.com/Lifelong-Robot-Learning/LIBERO)
소스의 수정분이며, 원본 코드 일부를 포함한다.

> MIT License
> Copyright (c) 2023 Lifelong Robot Learning

원본 라이선스 전문은 서브모듈의 `LIBERO/LICENSE` 에 있다.
이 패치를 단독으로 재배포할 때는 위 고지를 함께 유지할 것.

## 적용 대상 커밋

`8f1084e3132a39270c3a13ebe37270a43ece2a01` (2025-03-15)

다른 커밋에는 충돌할 수 있다. `setup.sh` 가 `git apply --check` 로 먼저 확인한다.
