import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:google_fonts/google_fonts.dart';
import 'profile_form_screen.dart';

void main() async {
  // Asegura que los canales nativos de Flutter estén completamente listos
  WidgetsFlutterBinding.ensureInitialized();

  try {
    // Inicializa Firebase de forma manual usando tus datos de proyecto
    await Firebase.initializeApp(
      options: const FirebaseOptions(
        apiKey: "AIzaSyA-provisional-key-puedes-dejarla-asi",
        appId: "1:nutritrack-android-app",
        messagingSenderId: "1234567890",
        projectId: "nutritrack-4aac7", // El ID de tu proyecto Firebase
      ),
    );
  } catch (e) {
    // Evita que la app se rompa si Firebase ya fue inicializado previamente
    print("Nota sobre la inicialización de Firebase: $e");
  }

  runApp(const NutriTrackApp());
}

class NutriTrackApp extends StatelessWidget {
  const NutriTrackApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      debugShowCheckedModeBanner: false,
      title: 'NutriTrack',
      theme: ThemeData(
        useMaterial3: true,
        colorSchemeSeed:
            Colors.green, // Identidad visual verde para salud/nutrición
        textTheme: GoogleFonts.latoTextTheme(),
      ),
      home: const WelcomeScreen(),
    );
  }
}

class WelcomeScreen extends StatelessWidget {
  const WelcomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        width: double.infinity,
        padding: const EdgeInsets.all(24),
        color: Colors.green.shade50,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.analytics_outlined, size: 90, color: Colors.green),
            const SizedBox(height: 20),
            Text(
              'NUTRITRACK',
              style: GoogleFonts.playfairDisplay(
                fontSize: 42,
                fontWeight: FontWeight.bold,
                color: Colors.green.shade900,
                letterSpacing: 1.5,
              ),
            ),
            const SizedBox(height: 8),
            const Text(
              'Nutrición Inteligente, Vida Equilibrada',
              style: TextStyle(
                fontSize: 16,
                fontStyle: FontStyle.italic,
                color: Colors.green,
              ),
            ),
            const SizedBox(height: 60),
            ElevatedButton.icon(
              onPressed: () {
                // Navegación fluida hacia tu formulario de perfil
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const ProfileFormScreen(),
                  ),
                );
              },
              icon: const Icon(Icons.arrow_forward),
              label: const Text('Comenzar Configuración'),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.green.shade700,
                foregroundColor: Colors.white,
                padding: const EdgeInsets.symmetric(
                  horizontal: 40,
                  vertical: 16,
                ),
                textStyle: const TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                ),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
