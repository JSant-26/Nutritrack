import 'package:flutter/material.dart';
import 'firestore_service.dart';

class ProfileFormScreen extends StatefulWidget {
  const ProfileFormScreen({super.key});

  @override
  State<ProfileFormScreen> createState() => _ProfileFormScreenState();
}

class _ProfileFormScreenState extends State<ProfileFormScreen> {
  final _formKey = GlobalKey<FormState>();

  // Controladores para capturar el texto de los inputs
  final _ageController = TextEditingController();
  final _weightController = TextEditingController();
  final _heightController = TextEditingController();

  String _gender = 'Masculino';
  double _activityLevel = 1.2; // Sedentario por defecto
  double? _calculatedBMR;

  // Lógica matemática: Fórmula de Mifflin-St Jeor
  final FirestoreService _firestoreService =
      FirestoreService(); // Instancia el servicio

  void _calculateMetabolism() async {
    if (_formKey.currentState!.validate()) {
      final double weight = double.parse(_weightController.text);
      final double height = double.parse(_heightController.text);
      final int age = int.parse(_ageController.text);

      double bmr;
      if (_gender == 'Masculino') {
        bmr = (10 * weight) + (6.25 * height) - (5 * age) + 5;
      } else {
        bmr = (10 * weight) + (6.25 * height) - (5 * age) - 161;
      }

      final double finalTdee = bmr * _activityLevel;

      setState(() {
        _calculatedBMR = finalTdee;
      });

      // 2. ENVIAR A FIRESTORE
      // Mostramos un SnackBar para avisar al usuario que se está procesando
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Guardando perfil en la nube...')),
      );

      await _firestoreService.saveUserProfile(
        userId: 'test_user_123', // ID provisional de pruebas
        age: age,
        weight: weight,
        height: height,
        gender: _gender,
        activityLevel: _activityLevel,
        tdee: finalTdee,
      );

      // Confirmación de éxito
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(
          content: Text('¡Perfil guardado exitosamente!'),
          backgroundColor: Colors.green,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Configura tu Perfil'),
        backgroundColor: Colors.green.shade700,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(24.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              const Text(
                'Necesitamos unos datos para calcular tus requerimientos calóricos diarios.',
                style: TextStyle(fontSize: 16, color: Colors.grey),
              ),
              const SizedBox(height: 24),

              // Input Edad
              TextFormField(
                controller: _ageController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Edad (años)',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.calendar_today),
                ),
                validator: (value) => value!.isEmpty ? 'Ingresa tu edad' : null,
              ),
              const SizedBox(height: 16),

              // Input Peso
              TextFormField(
                controller: _weightController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Peso (kg)',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.fitness_center),
                ),
                validator: (value) => value!.isEmpty ? 'Ingresa tu peso' : null,
              ),
              const SizedBox(height: 16),

              // Input Altura
              TextFormField(
                controller: _heightController,
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  labelText: 'Altura (cm)',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.height),
                ),
                validator: (value) =>
                    value!.isEmpty ? 'Ingresa tu altura' : null,
              ),
              const SizedBox(height: 16),

              // Dropdown Género
              DropdownButtonFormField<String>(
                value: _gender,
                decoration: const InputDecoration(
                  labelText: 'Género',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.people),
                ),
                items: ['Masculino', 'Femenino'].map((String val) {
                  return DropdownMenuItem<String>(value: val, child: Text(val));
                }).toList(),
                onChanged: (value) => setState(() => _gender = value!),
              ),
              const SizedBox(height: 16),

              // Dropdown Actividad Física
              DropdownButtonFormField<double>(
                value: _activityLevel,
                decoration: const InputDecoration(
                  labelText: 'Nivel de Actividad',
                  border: OutlineInputBorder(),
                  prefixIcon: Icon(Icons.directions_run),
                ),
                items: const [
                  DropdownMenuItem(
                    value: 1.2,
                    child: Text('Sedentario (Poco ejercicio)'),
                  ),
                  DropdownMenuItem(
                    value: 1.375,
                    child: Text('Ligero (1-3 días/semana)'),
                  ),
                  DropdownMenuItem(
                    value: 1.55,
                    child: Text('Moderado (3-5 días/semana)'),
                  ),
                  DropdownMenuItem(
                    value: 1.725,
                    child: Text('Intenso (6-7 días/semana)'),
                  ),
                ],
                onChanged: (value) => setState(() => _activityLevel = value!),
              ),
              const SizedBox(height: 32),

              // Botón Calcular
              ElevatedButton(
                onPressed: _calculateMetabolism,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                child: const Text(
                  'Calcular y Guardar',
                  style: TextStyle(fontSize: 16),
                ),
              ),

              // Mostrar Resultado si existe
              if (_calculatedBMR != null) ...[
                const SizedBox(height: 32),
                Card(
                  color: Colors.green.shade100,
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      children: [
                        const Text(
                          'Tu Gasto Energético Total Diario (TDEE):',
                          style: TextStyle(fontSize: 16),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          '${_calculatedBMR!.toStringAsFixed(0)} kcal',
                          style: const TextStyle(
                            fontSize: 28,
                            fontWeight: FontWeight.bold,
                            color: Colors.green,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }
}
