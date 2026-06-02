import 'package:cloud_firestore/cloud_firestore.dart';

class FirestoreService {
  // Instancia de la base de datos de Firestore
  final FirebaseFirestore _db = FirebaseFirestore.instance;

  // Función para guardar los datos antropométricos del usuario
  Future<void> saveUserProfile({
    required String userId,
    required int age,
    required double weight,
    required double height,
    required String gender,
    required double activityLevel,
    required double tdee,
  }) async {
    try {
      await _db.collection('users').doc(userId).set(
        {
          'age': age,
          'weight': weight,
          'height': height,
          'gender': gender,
          'activityLevel': activityLevel,
          'tdee': tdee,
          'updatedAt':
              FieldValue.serverTimestamp(), // Almacena la fecha de guardado
        },
        SetOptions(merge: true),
      ); // Usa merge para actualizar solo campos modificados sin borrar otros
    } catch (e) {
      print("Error al guardar en Firestore: $e");
      rethrow;
    }
  }
}
