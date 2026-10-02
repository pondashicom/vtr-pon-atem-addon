# 配布条件・第三者通知 — 0.3.0

## 自作コード

Copyright (c) 2026 Tetsu Suzuki. 自作コードは[MIT License](MIT.txt)です。原文の著作権・許諾通知を保持してください。無保証・責任制限は原文によります。利用者の制作目的に非商用限定の条件を追加しません。

## インストール時の同意

パッケージのMIT原文を本体が同意対象として表示します。通知は別に閲覧できます。拒否・取り消しではそのパッケージを適用しません。更新版では文書と同意を改めて確認します。これによってMITやLGPLで認められた権利を減らすものではありません。

## 外部ソフト

Blackmagic ATEM Switchers Software 10.4 x64を、[Blackmagic Design公式サポート](https://www.blackmagicdesign.com/support/family/atem-live-production-switchers)から別途導入してください。ATEMのファームウェアは同ソフトと互換のある版を使用します。

ATEM Software、NDI Runtime／Tools、Desktop Video、利用者のVST3プラグインはこのパッケージに含まれません。外部ソフトを導入するときはその提供元の契約を確認・承諾してください。アドオンの同意操作は外部インストーラーの同意を代行しません。SDKは生成する開発者だけが別途取得して契約を確認します。

## 生成元と境界

使用するSDKは Blackmagic Switchers SDK 10.4。配置は `switcher-addons/vtr-pon-atem-addon.dll`、実行契約は `switcher-addon-abi-v1`、Runtime Status v1です。DeckLinkの追加Output ABIはv1です。

SDK本体、生成ヘッダー、IDL、サンプル、テストDLL、デバッグ情報、ベンダーRuntime、他者のプラグインは配布しません。SDK由来の必要なコード・通知と、次項の同梱依存の条件を自作MITと区別します。

## Blackmagic Switchers SDK 10.4

MIDL生成宣言からの機械実行コードを含みます。[SDK通知原文](third-party/ATEM-SDK-NOTICE.txt)の許諾・通知保持条項と、機械実行コードだけのコピーの例外に従います。Software／機器の名称はBlackmagic Designの名称・商標です。SDKとSoftwareは[公式サポート](https://www.blackmagicdesign.com/support/family/atem-live-production-switchers)から取得します。
