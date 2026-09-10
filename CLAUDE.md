# CLAUDE.md

LIBERO 벤치마크를 VLA 연구용으로 쓰기 위한 작업 저장소.
업스트림 LIBERO는 **2025-03-15(`8f1084e`) 이후 멈춰 있고**, 그대로는 최신 환경에서 동작하지 않는다.
이 저장소는 그 간극을 메우는 설치 스크립트·패치·탐색 도구와, 조사해서 **직접 검증한 사실들**을 담는다.

## 저장소에 없는 것

`.gitignore`로 제외된 것들이며, `setup.sh`로 재현한다.
`LIBERO/`는 **서브모듈**이라 커밋(`8f1084e`)이 고정되어 있지만, 내용은 클론해야 채워진다.

| 경로 | 무엇 | 왜 제외 |
|---|---|---|
| `.venv/` | Python 3.10 환경 | 1.8 GB |
| `datasets/` | 데모 hdf5 | 100 GB. **평가만 하면 불필요** |
| `demonstration_data/` | 직접 수집한 시연 | 실험 산출물 |

## 시작하기

```bash
git clone --recursive <이 저장소>        # 서브모듈까지 함께
./setup.sh                              # 환경 · 패치 · 설정 파일
.venv/bin/python run_demo.py --list     # 태스크 목록
.venv/bin/python run_demo.py --suite libero_spatial --task 0 --gui
```

데이터셋이 필요할 때만 (학습용):
```bash
# --datasets all 은 쓰지 말 것 (아래 "업스트림 버그" 참고)
.venv/bin/python -c "
from libero.libero.utils.download_utils import download_from_huggingface
import os
D = os.path.expanduser('~/Desktop/libero/datasets')
for n in ['libero_spatial','libero_object','libero_goal','libero_10','libero_90']:
    download_from_huggingface(dataset_name=n, download_dir=D, check_overwrite=False)
"
```

## 실행 환경

| | macOS (M4) | 5090 서버 |
|---|---|---|
| 렌더 백엔드 | CGL | EGL (`MUJOCO_GL=egl`) |
| 속도 | 22.6 steps/sec | **118.7 steps/sec** |
| 경로 | `~/Desktop/libero` | `~/libero` |
| 데이터셋 | 없음 | 94 GB (5개 스위트 전부) |

5090 접속은 `ssh 5090`. 무거운 실험은 그쪽에서 돌린다.
`replay_demo.py`는 데이터셋이 있는 5090에서 쓴다.

## 업스트림 버그 — 마주치면 이 목록을 먼저 볼 것

세션 중 발견해 확인한 것들. **전부 업스트림에 그대로 남아 있다.**

| # | 증상 | 원인 | 대응 |
|---|---|---|---|
| 1 | `ModuleNotFoundError: libero` | `setup.py`의 `find_packages()`가 네임스페이스 패키지를 못 잡음 | `.pth`로 경로 주입 (`setup.sh`) |
| 2 | `UnpicklingError` | torch 2.6부터 `torch.load` 기본값 변경 | `weights_only=False` (패치) |
| 3 | `libero_90` 데이터가 안 받아짐 | `--datasets all`이 HF에 없는 `libero_100`을 찾음. **에러 없이 조용히 누락** | 스위트를 하나씩 지정 |
| 4 | `KeyError: 'MountedP'` | `--robots`가 `nargs="+"`인데 기본값이 문자열 `"Panda"` | `--robots Panda` 명시 |
| 5 | `add_keypress_callback() takes 2 args` | 옛 robosuite 시그니처 | 콜백 등록 3줄 제거 (패치) |
| 6 | `AssertionError` in `get_joint_qpos_addr` | robosuite 1.4.1 ↔ mujoco 3.x 비호환 | `mujoco==2.3.7` 고정 |
| 7 | macOS: `dlopen OpenGL` 실패 | mujoco 2.3.7이 옛 경로 하드코딩 (3.0.0에서 수정) | `cgl.py` 경로 치환 (`setup.sh`) |
| 8 | macOS: `egl_probe` 빌드 실패 | Linux 전용인데 robomimic이 무조건 요구 | `--no-deps` 설치 |

**의존성이 선언되어 있지 않다.** `libero`의 `install_requires=[]`라 `pip install -e`가 아무것도 끌어오지 않고, 버전 충돌도 막아주지 않는다. `setup.sh`가 전부 명시한다.

## 검증된 사실

추측이 아니라 코드·데이터를 직접 확인한 것만 적는다. 재확인이 필요하면 근거 위치를 따라가면 된다.

### 벤치마크 구성
- **130 태스크** = spatial 10 · object 10 · goal 10 · **libero_90** 90 · libero_10 10
- 태스크당 **평가 초기상태 50개**(`.pruned_init`, 저장소 포함) + **데모 50개**(hdf5, 별도) — 총 6,500 데모
- **평가에는 데모가 필요 없다.** 저장소 651 MB만으로 채점 가능. 100 GB는 학습용
- 두 50개는 **서로 다른 표본**이다. 일치하는 것이 0개 — 정책은 데모에서 본 적 없는 배치에서 평가받는다
- bddl은 좌표가 아니라 **영역**을 적고, 그 안에서 표집해 50가지가 나온다 (물체 위치 1~2 cm 흔들림)

### 성공 판정
- 술어 **8개**(`On`·`In`·`Open`·`Close`·`TurnOn`·`TurnOff`·`Up`·`true`)를 130 태스크가 조합만 한다. 태스크별 구현 없음
- `On` = 높이 + 접촉 + **수평 거리 3 cm** 세 조건. `Open`/`TurnOn`은 접촉을 안 보고 `qpos`를 읽는다
- **실패 신호는 없다.** `done`은 horizon 도달만 본다. 성공은 순간 판정이라 유지 요구가 없다
- 평가 코드는 매 스텝 `env.env._check_success()`를 직접 확인해야 한다. `done`만 보면 놓친다

### 물리·상태
- 행동 `(7,)` = 이동 3(m) + 회전 3(rad, 축-각도) + 그리퍼 1. **전부 `[-1, 1]` 정규화된 증분**
- `[-1,1]` → 위치 `[-0.05, 0.05] m`. 범위 밖은 잘린다. **한 스텝 이동량이 아니라 목표**다
- 그리퍼는 `np.sign()`만 사용 — 부호만 유효. 완전히 닫히는 데 100스텝
- 행동 7 → OSC → `d.ctrl` 9(토크 7 + 집게 위치 2). **역기구학 단계가 없다.** `τ = JᵀF + 중력보상`
- 상태 92 = `1 + qpos 48 + qvel 43` — **`libero_spatial` 전용 숫자.** 130 태스크 전체로는 45~123
- `qvel`의 **각속도만 물체 좌표계**, 나머지는 월드. 관성이 물체 좌표계에서 상수이기 때문
- 물리는 완전히 결정론적(재실행 시 차이 `0.000e+00`). 실패는 접촉의 불연속에서 온다

### VLA 관행 (π₀ 사례로 검증)
- 배포 체크포인트는 **4개 스위트(40 태스크)로만** 학습·평가. `libero_90` 미포함
- 학습 데이터는 원본 50개가 아니라 **1,693개**(2,000개 중 15% 제외). 거른 주체는 **OpenVLA 팀**(`openvla/modified_libero_rlds`의 `no_noops`)
- `no_noops`는 정지 프레임을 제거해 **궤적 길이도 바꾼다** — 원본에 없던 길이가 생긴다
- 보고 성적: spatial 98.8 / object 98.2 / goal 98.0 / 10: 92.4 → 평균 **96.85%**
- 같은 체크포인트가 `libero_90`에서는 **18%** ([openpi #734](https://github.com/Physical-Intelligence/openpi/issues/734))
- 평가 설정: 롤아웃 **50회**(저장소 기본 20 아님), `max_steps`는 스위트별 **220~520**(기본 600 아님). 학습 데모 최대 길이 + 10% 안팎

## 작업 방침

- **수치를 추측하지 말 것.** 이 저장소의 값들은 전부 실측이다. 새 주장을 추가할 때도 근거를 함께 남긴다
- 웹 검색 요약은 **파일 원문과 어긋나는 경우가 있었다.** 세부 수치는 raw 파일을 직접 확인한다
- **`LIBERO/`는 서브모듈이라 수정사항을 담지 못한다.** 업스트림 커밋만 가리킨다.
  로컬 수정은 반드시 `patches/`로 뽑아 두고 `setup.sh`가 적용하게 한다 —
  그러지 않으면 다른 곳에서 받았을 때 패치 없는 원본이 나온다
- `git status`에서 `LIBERO (modified content)`로 보이는 것은 **정상**이다. 패치가 적용된 상태라는 뜻
- 무거운 실험(학습·대량 평가)은 5090에서. 맥은 개발·시각화용

## 다음에 할 만한 것

- [ ] `libero_90`을 **홀드아웃 평가**로 사용 — 배포 모델이 18%라 개선 폭이 드러난다. `.pruned_init` 90개(8.8 MB)만 있으면 되고 데모는 불필요
- [ ] 데모 50개를 `actions` 모드로 재생해 **버전 차이로 인한 재현 실패율** 통계
- [ ] VLA 모델 연결 — 5090 32 GB면 7B 추론 여유. `run_demo.py:52`의 무작위 행동 자리를 대체
- [ ] `openvla/modified_libero_rlds`를 원본과 대조해 **`no_noops` 필터 기준 확정** (논문 부록 E에만 서술됨)
