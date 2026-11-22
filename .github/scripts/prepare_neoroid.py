from pathlib import Path
import sys

root = Path(sys.argv[1]).resolve()

def replace_once(path, old, new):
    data = path.read_text(encoding="utf-8")
    if data.count(old) != 1:
        raise SystemExit(f"Patch anchor mismatch in {path}: expected one match")
    path.write_text(data.replace(old, new, 1), encoding="utf-8")

gradle = root / "app/app/build.gradle.kts"
replace_once(gradle, 'applicationId = "de.mm20.launcher2"', 'applicationId = "com.redy.neoroid"')
replace_once(gradle, 'versionName = "1.41.0"', 'versionName = "0.1"')
replace_once(gradle, '        release {\n            applicationIdSuffix = ".release"', '        release {')

for rel in (
    "core/base/src/main/res/values/strings.xml",
    "core/base/src/debug/res/values/strings.xml",
    "core/base/src/nightly/res/values/strings.xml",
):
    p = root / rel
    if p.exists():
        s = p.read_text(encoding="utf-8")
        s = s.replace("Kvaesitso Debug", "Neoroid Test")
        s = s.replace("Kvaesitso Nightly", "Neoroid Nightly")
        s = s.replace("Kvaesitso", "Neoroid")
        p.write_text(s, encoding="utf-8")

shared = root / "app/ui/src/main/java/de/mm20/launcher2/ui/launcher/SharedLauncherActivity.kt"
replace_once(
    shared,
    "        super.onCreate(savedInstanceState)\n\n        if (savedInstanceState != null) {",
    """        super.onCreate(savedInstanceState)

        if (mode == LauncherActivityMode.Launcher &&
            !getSharedPreferences("neoroid_setup", MODE_PRIVATE).getBoolean("complete", false)
        ) {
            startActivity(Intent(this, NeoroidWelcomeActivity::class.java))
            finish()
            return
        }

        if (savedInstanceState != null) {"""
)

welcome = root / "app/ui/src/main/java/de/mm20/launcher2/ui/launcher/NeoroidWelcomeActivity.kt"
welcome.parent.mkdir(parents=True, exist_ok=True)
welcome.write_text(r'''package de.mm20.launcher2.ui.launcher

import android.app.role.RoleManager
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Settings
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp

class NeoroidWelcomeActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            NeoroidWelcomeScreen(
                onOpenWebsite = { url -> startActivity(Intent(Intent.ACTION_VIEW, Uri.parse(url))) },
                onContinue = { continueSetup() }
            )
        }
    }

    private fun continueSetup() {
        getSharedPreferences("neoroid_setup", MODE_PRIVATE)
            .edit().putBoolean("complete", true).apply()

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            val roles = getSystemService(RoleManager::class.java)
            if (roles != null && roles.isRoleAvailable(RoleManager.ROLE_HOME) &&
                !roles.isRoleHeld(RoleManager.ROLE_HOME)
            ) {
                startActivityForResult(roles.createRequestRoleIntent(RoleManager.ROLE_HOME), 410)
                return
            }
        } else {
            startActivity(Intent(Settings.ACTION_HOME_SETTINGS))
        }
        openLauncher()
    }

    @Deprecated("Deprecated in Android API")
    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == 410) openLauncher()
    }

    private fun openLauncher() {
        startActivity(Intent(this, LauncherActivity::class.java).addFlags(
            Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_NEW_TASK
        ))
        finish()
    }
}

@Composable
private fun NeoroidWelcomeScreen(onOpenWebsite: (String) -> Unit, onContinue: () -> Unit) {
    val blue = Color(0xFF4388FF)
    Surface(Modifier.fillMaxSize(), color = Color(0xFF0B1020)) {
        Column(
            Modifier.fillMaxSize().verticalScroll(rememberScrollState())
                .padding(horizontal = 24.dp, vertical = 28.dp),
            verticalArrangement = Arrangement.Center,
            horizontalAlignment = Alignment.Start
        ) {
            Box(
                Modifier.size(64.dp).clip(RoundedCornerShape(20.dp)).background(blue),
                contentAlignment = Alignment.Center
            ) {
                Text("N", color = Color.White, fontSize = 34.sp, fontWeight = FontWeight.Bold)
            }
            Spacer(Modifier.height(28.dp))
            Text("Welcome to Neoroid", color = Color.White, fontSize = 30.sp,
                lineHeight = 36.sp, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(8.dp))
            Text("A fresh, focused home for your Android.",
                color = Color(0xFFB7C1D6), fontSize = 16.sp)
            Spacer(Modifier.height(32.dp))
            Text("GET STARTED", color = Color(0xFF91A9D2), fontSize = 12.sp,
                fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(12.dp))
            SiteButton("Voltra", Color(0xFFE8752A)) { onOpenWebsite("https://voltra.tv/") }
            Spacer(Modifier.height(10.dp))
            SiteButton("Morphe", Color(0xFF3478E5)) { onOpenWebsite("https://morphe.software/") }
            Spacer(Modifier.height(10.dp))
            SiteButton("MicroG", Color(0xFFD94B4B)) {
                onOpenWebsite("https://morphe.software/microg")
            }
            Spacer(Modifier.height(28.dp))
            Button(
                onClick = onContinue,
                modifier = Modifier.fillMaxWidth().height(58.dp),
                shape = RoundedCornerShape(16.dp),
                colors = ButtonDefaults.buttonColors(containerColor = blue, contentColor = Color.White)
            ) {
                Text("Continue", fontSize = 16.sp, fontWeight = FontWeight.SemiBold)
            }
            Spacer(Modifier.height(12.dp))
            Text("You can continue even if you haven't opened these websites.",
                color = Color(0xFF8793AA), fontSize = 12.sp)
        }
    }
}

@Composable
private fun SiteButton(label: String, color: Color, onClick: () -> Unit) {
    Button(
        onClick = onClick,
        modifier = Modifier.fillMaxWidth().height(54.dp),
        shape = RoundedCornerShape(14.dp),
        colors = ButtonDefaults.buttonColors(containerColor = color, contentColor = Color.White)
    ) {
        Text(label, fontSize = 15.sp, fontWeight = FontWeight.SemiBold)
    }
}
''', encoding="utf-8")

manifest = root / "app/ui/src/main/AndroidManifest.xml"
replace_once(
    manifest,
    "    <application>\n",
    """    <application>
        <activity
            android:name=".launcher.NeoroidWelcomeActivity"
            android:exported="false"
            android:theme="@style/LauncherTheme" />
"""
)
print("Neoroid source patch applied.")

# Tighten Neoroid's merged app permissions and legacy application settings.
main_manifest = root / "app/app/src/main/AndroidManifest.xml"
main_data = main_manifest.read_text(encoding="utf-8")
for permission in (
    '    <uses-permission android:name="android.permission.GET_ACCOUNTS" />\n',
    '    <uses-permission android:name="android.permission.WRITE_CALENDAR" />\n',
    '    <uses-permission android:name="android.permission.MANAGE_EXTERNAL_STORAGE" />\n',
    '    <uses-permission android:name="android.permission.ACCESS_MEDIA_LOCATION" />\n',
    '    <uses-permission android:name="android.permission.REQUEST_INSTALL_PACKAGES" />\n',
    '    <uses-permission android:name="android.permission.INTERACT_ACROSS_PROFILES" />\n',
    '    <uses-permission android:name="android.permission.REQUEST_DELETE_PACKAGES" />\n',
):
    main_data = main_data.replace(permission, "")
main_data = main_data.replace('android:allowBackup="true"', 'android:allowBackup="false"')
for legacy_attribute in (
    '        android:fullBackupContent="true"\n',
    '        android:crossProfile="true"\n',
    '        android:requestLegacyExternalStorage="true"\n',
    '        android:usesCleartextTraffic="true"\n',
):
    main_data = main_data.replace(legacy_attribute, "")
main_manifest.write_text(main_data, encoding="utf-8")

# The UI module duplicated permissions already declared by app/features.
ui_manifest = root / "app/ui/src/main/AndroidManifest.xml"
ui_data = ui_manifest.read_text(encoding="utf-8")
ui_data = ui_data.replace('    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />\\n', "")
ui_data = ui_data.replace('    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE" />\\n', "")
ui_manifest.write_text(ui_data, encoding="utf-8")
