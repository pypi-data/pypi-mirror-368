//@ts-check
import fs from 'fs'
import process from 'process'

/**
 * Check if the Python virtual environment site-packages directory is available at `.venv/lib/site-packages` (e.g. on Windows).
 * If not (e.g. on Linux), search for the actual site-packages directory and create a symbolic link at `.venv/lib/site-packages`.
 * 
 * This function is usefull when copied into a preinstall npm script, to allow a Django project to access the other scripts and assets provided by zut.
 * 
 * @param {string?} venvDir
 */
export function ensurePythonVenv(venvDir = null) {
    if (! venvDir) {
        venvDir = `${process.cwd()}/.venv`
    }
    const venvLibDir = `${venvDir}/lib`
    if (! fs.existsSync(venvLibDir)) {
        throw new Error(`Python venv libraries not found at ${venvLibDir}. Is venv installed?`)
    }

    const fixedDir = `${venvLibDir}/site-packages`
    if (fs.existsSync(fixedDir)) {
        return
    }

    for (const versionName of fs.readdirSync(venvLibDir)) {
        const versionDir = `${venvLibDir}/${versionName}/site-packages`
        if (fs.existsSync(versionDir)) {
            console.log(`Create symlink ${fixedDir} pointing to ${versionDir}`)
            fs.symlinkSync(versionDir, fixedDir)
        }
    }
}
