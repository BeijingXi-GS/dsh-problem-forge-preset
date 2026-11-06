/**
 * 把本仓库 skills/ 目录的绝对路径写入 cordis.patch.yml 的 bundledSkillDir。
 *
 * DSH 的 skill-filesystem 会用 path.resolve() 解析 bundledSkillDir（相对路径按
 * 进程 cwd 解析，不可靠），所以必须写入绝对路径。仓库里该行默认是注释掉的，
 * 运行本脚本后自动取消注释并写入当前机器上的真实路径。
 *
 * 用法（在仓库根目录）：
 *   node scripts/set-skill-dir.mjs
 */
import { readFile, writeFile } from 'node:fs/promises'
import { dirname, join, resolve } from 'node:path'
import { fileURLToPath } from 'node:url'

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const skillsDir = join(repoRoot, 'skills')
const patchFile = join(repoRoot, 'cordis.patch.yml')

const raw = await readFile(patchFile, 'utf8')
const value = `bundledSkillDir: '${skillsDir.replace(/\\/g, '/')}'`

// 允许三种现状：已注释的 bundledSkillDir / 未注释的 bundledSkillDir / 完全没有。
// 关键点：替换时必须保留原有的行首缩进，否则这个键会被写到 YAML 顶层，
// 整份 cordis.patch.yml 都会解析失败。
const commented = /^([ \t]*)#[ \t]*bundledSkillDir:.*$/m
const active = /^([ \t]*)bundledSkillDir:.*$/m

let out
if (commented.test(raw)) {
  out = raw.replace(commented, (_m, indent) => indent + value)
} else if (active.test(raw)) {
  out = raw.replace(active, (_m, indent) => indent + value)
} else {
  // 兜底：插到 skill-filesystem 的 config 块里（缩进与同块其它键对齐）
  out = raw.replace(
    /(name: '@deepseek-ai\/dsh-skill-filesystem'\s*\n\s*config:\s*\n)/,
    `$1              ${value}\n`,
  )
  if (out === raw) {
    console.error('未找到 skill-filesystem 配置块，请手动把下面这行加进 cordis.patch.yml：')
    console.error(`  ${value}`)
    process.exit(1)
  }
}

await writeFile(patchFile, out, 'utf8')
console.log(`已写入 ${patchFile}`)
console.log(`  ${value}`)
console.log('下一步：plugin_manager action=install_bundle target="<本仓库绝对路径>"，然后新建会话。')