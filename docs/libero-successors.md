# LIBERO 후속 벤치마크

원본 LIBERO 이후 나온 확장판 정리. 전부 "평가 방식이 성능을 부풀린다"는 같은 문제의식에서 출발한다.

조사 시점 2026-09-11. 발표 학회는 확인된 것만 적었고, 나머지는 프리프린트 상태다.

## 계보

| 이름 | 발표 | 시기 | 초점 | 코드 |
|---|---|---|---|---|
| **LIBERO** | NeurIPS 2023 D&B | 2023-06 | 원본. 평생학습용 130 태스크 | [Lifelong-Robot-Learning/LIBERO](https://github.com/Lifelong-Robot-Learning/LIBERO) |
| **LIBERO-PRO** | 프리프린트 | 2025-10 (v2 2026-05) | 암기 폭로. 5개 축 조합 | [Zxy-MLlab/LIBERO-PRO](https://github.com/Zxy-MLlab/LIBERO-PRO) |
| **LIBERO-Plus** | **CVPR 2026** | 2025-10 | 축별 취약점 진단. 7개 축 | [sylvestf/LIBERO-plus](https://github.com/sylvestf/LIBERO-plus) |
| **LIBERO-X** | **RSS 2026** | 2026-02 | 계층적 난이도 + 신규 데모 | 미공개 |
| **LIBERO-Para** | 프리프린트 | 2026-03 | 패러프레이즈만 분리 | [cau-hai-lab/LIBERO-Para](https://github.com/cau-hai-lab/LIBERO-Para) |

원본 LIBERO는 평생학습(lifelong learning) 벤치마크로 만들어졌다. VLA 평가용으로 쓰이는 건 나중에 생긴 관행이고, 후속 연구들이 문제 삼는 것도 그 관행이다.

## 왜 후속 연구가 쏟아졌나

공개된 VLA 체크포인트들이 4개 스위트에서 90%를 넘긴다. 그런데 같은 체크포인트가 `libero_90`에서는 18%로 떨어진다
([openpi #734](https://github.com/Physical-Intelligence/openpi/issues/734)).

원인은 평가 설계에 있다. 평가용 초기 상태 50개와 학습용 데모 50개는 서로 겹치지 않지만, 둘 다 **같은 방, 같은 물체, 같은 지시문**에서 나온다. 물체가 1~2 cm 움직이는 정도의 차이다. 모델이 장면을 이해했는지 궤적을 외웠는지 구분할 수 없다.

후속 벤치마크들은 여기에 의도적인 교란을 넣는다.

## LIBERO-PRO

[arXiv 2510.03827](https://arxiv.org/abs/2510.03827) · 화중과기대(HUST) 외 · 315 stars

가장 공격적이다. 초록의 문장이 그대로 결론이다.

> 기존 모델들은 표준 LIBERO 평가에서 90% 이상을 달성하지만, 일반화 설정에서는 **0.0%로 붕괴한다.**

교란 축 5개: Object(외형·색·크기), Position(위치 재배치), Semantic(지시문 패러프레이즈), Task(목표 상태 재정의), Environment(작업 공간 교체). 임의 조합이 가능하다.

관찰된 실패 양상이 구체적이다.

- 목표 물체를 무관한 물건으로 바꿔도 계속 잡으려 든다
- 지시문을 망가뜨리거나 의미 없는 토큰을 넣어도 출력이 변하지 않는다

평가 모델 7종 평균: Pi0.5 0.53 / OpenVLA 0.52 / x-VLA 0.46 / Pi0 0.44 / MolmoAct 0.41 / NORA 0.40.

**한계**: 결론이 이진에 가깝다. "붕괴한다"는 알려주지만 무엇을 고쳐야 하는지는 알려주지 않는다. 설치 요구사항도 Python 3.8.13 / PyTorch 1.11.0이라 최신 환경과 충돌한다.

## LIBERO-Plus

[arXiv 2510.13626](https://arxiv.org/abs/2510.13626) · CVPR 2026 · 443 stars

제목이 두 개다. arXiv는 "In-depth Robustness Analysis of Vision-Language-Action Models",
CVPR 게재본은 "A Progressive Robustness Benchmark for Visual-Language-Action Models".
검색할 때 헷갈릴 수 있다.

교란을 **축별로 분해**해서 어느 입력에 약한지 짚는다. 7개 축을 다시 21개 세부 요소로 나눈다.

| 축 | 내용 |
|---|---|
| Objects Layout | 방해 물체 추가, 목표 물체 이동 |
| Camera Viewpoints | 위치, 방향, 화각 |
| Robot Initial States | 매니퓰레이터 자세 |
| Language Instructions | LLM 기반 재작성 |
| Light Conditions | 세기, 방향, 색, 그림자 |
| Background Textures | 장면·표면 외형 |
| Sensor Noise | 광도 왜곡, 이미지 열화 |

총 10,030개 태스크. 결과 중 두 가지가 특히 유용하다.

- **카메라 시점과 로봇 초기 자세**에서 95% → 30% 이하로 급락한다
- **언어 변형에는 거의 반응하지 않는다.** 추가 실험 결과 모델이 지시문을 사실상 무시하는 것으로 나타났다

두 번째가 중요하다. LIBERO-PRO의 "망가진 지시문에도 출력이 같다"와 같은 현상을 반대편에서 확인한 셈이다. 언어 조건부 정책이라면서 언어를 안 본다는 뜻이다.

**제공물**: 11개 모델 리더보드(최고 OpenVLA-OFT+ 79.6%), 파인튜닝된 OpenVLA-OFT+ 가중치, RLDS·LeRobot 데이터셋.

## LIBERO-X

[arXiv 2602.06556](https://arxiv.org/abs/2602.06556) · RSS 2026

두 가지를 더한다.

1. **계층적 평가**. 난이도가 점진적으로 올라가며 공간 일반화, 물체 인식, 지시 이해를 나눠서 본다
2. **신규 학습 데이터**. 사람이 직접 조종한 데모로, 한 장면에서 여러 세부 목표를 지원한다

누적 교란에서 성능이 크게 떨어지며, 장면 이해와 지시 접지(grounding)의 한계를 드러낸다고 보고한다. 조사 시점 기준 코드는 공개되지 않았다.

## LIBERO-Para

[arXiv 2603.28301](https://arxiv.org/abs/2603.28301) · 중앙대 HAI Lab

언어 축 하나만 떼어내 정밀하게 본다. 행동 표현(action expression)과 물체 지칭(object reference)을 독립적으로 바꿔가며 어느 쪽에 둔감한지 분리한다.

LIBERO-Plus가 "언어를 무시한다"고 관찰한 것을 진단 도구로 만든 셈이다.

## 어느 것을 쓸까

**LIBERO-Plus**를 권한다.

| | LIBERO-PRO | LIBERO-Plus | LIBERO-X |
|---|---|---|---|
| 심사 통과 | 없음 | CVPR 2026 | RSS 2026 |
| 교란 축 | 5 | 7 (21 세부) | 계층적 |
| 규모 | 미명시 | 10,030 태스크 | 미명시 |
| 리더보드 | 7개 모델 | 11개 모델 | 없음 |
| 체크포인트 | 없음 | OpenVLA-OFT+ | 없음 |
| 학습 데이터 | 없음 | RLDS + LeRobot | 있음 |
| 코드 | 있음 | 있음 | 없음 |
| 요구 환경 | Python 3.8 / torch 1.11 | robosuite 1.4.0, bddl 1.0.1 | 불명 |

이유 셋.

1. **진단이 된다.** "0%"가 아니라 어느 축에서 무너지는지 알려준다. 다음 실험을 설계할 수 있다
2. **지금 환경에서 돌아갈 가능성이 높다.** robosuite 1.4.0 / bddl 1.0.1은 이 저장소의 핀(robosuite 1.4.1, bddl 1.0.1)과 거의 같다. README도 평가가 "almost identical to LIBERO"라고 한다. LIBERO-PRO의 Python 3.8 / torch 1.11은 이 저장소의 3.10 / torch 2.14와 충돌한다
3. **학습 없이 바로 평가할 수 있다.** 파인튜닝된 OpenVLA-OFT+ 가중치를 배포한다

순서는 LIBERO-Plus로 축별 취약점을 먼저 파악하고, 극단 케이스가 필요하면 LIBERO-PRO를 덧붙이는 쪽이 낫다.

## 숫자가 안 맞는 것처럼 보이는 이유

LIBERO-Plus 리더보드 최고점은 79.6%인데 LIBERO-PRO는 0.0%를 말한다. 모순이 아니라 교란 강도가 다르다.

- LIBERO-Plus 79.6%: 축별 평균, 단일 교란 위주
- LIBERO-PRO 0.0%: 특정 축의 극단 조합

논문을 인용할 때는 어느 설정의 숫자인지 같이 적어야 한다.

## 참고

- [LIBERO (NeurIPS 2023 D&B)](https://papers.nips.cc/paper_files/paper/2023/hash/8c3c666820ea055a77726d66fc7d447f-Abstract-Datasets_and_Benchmarks.html)
- [LIBERO-PRO (arXiv 2510.03827)](https://arxiv.org/abs/2510.03827)
- [LIBERO-Plus (arXiv 2510.13626)](https://arxiv.org/abs/2510.13626) · [CVPR 2026 Open Access](https://openaccess.thecvf.com/content/CVPR2026/html/Fei_LIBERO-Plus_A_Progressive_Robustness_Benchmark_for_Visual-Language-Action_Models_CVPR_2026_paper.html)
- [LIBERO-X (arXiv 2602.06556)](https://arxiv.org/abs/2602.06556) · [RSS 2026](https://roboticsconference.org/program/papers/97/)
- [LIBERO-Para (arXiv 2603.28301)](https://arxiv.org/abs/2603.28301)
- [openpi #734 — libero_90에서 18%](https://github.com/Physical-Intelligence/openpi/issues/734)
