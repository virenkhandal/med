"""Hand-curated knowledge base for the med-study PE exams.

Each section encodes structured, fact-level knowledge pulled directly from the
PDFs in /exams. Question generators in `questions.py` use this to produce
quizzes with real clinical content — not just "does this item belong to exam
X".
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Cranial nerves
# ---------------------------------------------------------------------------

CRANIAL_NERVES: list[dict] = [
    {
        "num": "I",
        "name": "Olfactory",
        "kind": "sensory",
        "tests": [
            "Ask patient to occlude one nostril and identify a familiar smell",
        ],
        "finding": "anosmia (loss of smell)",
    },
    {
        "num": "II",
        "name": "Optic",
        "kind": "sensory",
        "tests": [
            "Assess visual acuity using a Snellen pocket chart at 14 inches",
            "Assess visual fields by confrontation",
            "Perform a fundoscopic exam (optic disc, vessels, retina)",
        ],
        "finding": "decreased acuity, visual field defect, or abnormal fundoscopic findings",
    },
    {
        "num": "III",
        "name": "Oculomotor",
        "kind": "motor",
        "tests": [
            "Inspect pupil size and shape",
            "Assess direct and consensual pupillary reaction to light",
            "Assess pupillary convergence and accommodation",
            "Assess extraocular movements",
        ],
        "finding": "ptosis, mydriasis, 'down and out' eye position",
    },
    {
        "num": "IV",
        "name": "Trochlear",
        "kind": "motor",
        "tests": [
            "Assess extraocular movements (superior oblique — eye down and in)",
        ],
        "finding": "vertical diplopia worse on downgaze",
    },
    {
        "num": "V",
        "name": "Trigeminal",
        "kind": "both",
        "tests": [
            "Palpate temporal and masseter muscles as patient clenches teeth",
            "Assess light-touch sensation of the face in V1, V2, and V3 distributions",
        ],
        "finding": "facial numbness or jaw weakness",
    },
    {
        "num": "VI",
        "name": "Abducens",
        "kind": "motor",
        "tests": [
            "Assess lateral gaze of each eye",
        ],
        "finding": "inability to abduct the affected eye",
    },
    {
        "num": "VII",
        "name": "Facial",
        "kind": "motor",
        "tests": [
            "Observe face for asymmetry at rest",
            "Ask patient to raise eyebrows, frown, close eyes against resistance",
            "Ask patient to smile showing teeth and puff out cheeks",
        ],
        "finding": "unilateral facial droop, inability to close eye",
    },
    {
        "num": "VIII",
        "name": "Acoustic (Vestibulocochlear)",
        "kind": "sensory",
        "tests": [
            "Assess hearing by rubbing thumb and forefinger together 2 inches from each ear",
            "Perform a whisper test bilaterally",
            "Verbalize Weber and Rinne tests if hearing loss is detected",
        ],
        "finding": "unilateral hearing loss",
    },
    {
        "num": "IX",
        "name": "Glossopharyngeal",
        "kind": "both",
        "tests": [
            "Inspect symmetric rise of the soft palate with 'ahh'",
            "Verbalize testing the gag reflex with a tongue blade",
        ],
        "finding": "uvula deviation away from lesion",
    },
    {
        "num": "X",
        "name": "Vagus",
        "kind": "both",
        "tests": [
            "Inspect symmetric rise of the soft palate with 'ahh'",
            "Verbalize testing the gag reflex with a tongue blade",
        ],
        "finding": "hoarseness, dysphagia, palatal asymmetry",
    },
    {
        "num": "XI",
        "name": "Spinal Accessory",
        "kind": "motor",
        "tests": [
            "Assess sternocleidomastoid strength against resistance (head/neck rotation)",
            "Assess trapezius strength against resistance (shoulder shrug)",
        ],
        "finding": "weakness of shoulder shrug or head rotation",
    },
    {
        "num": "XII",
        "name": "Hypoglossal",
        "kind": "motor",
        "tests": [
            "Inspect the tongue for fasciculations or atrophy",
            "Assess that the tongue is midline when protruded",
        ],
        "finding": "tongue deviation toward the side of the lesion",
    },
]


# ---------------------------------------------------------------------------
# Dermatomes (from the Neuro checklist)
# ---------------------------------------------------------------------------

DERMATOMES: list[dict] = [
    {"level": "C5", "area": "Lateral upper arm"},
    {"level": "C6", "area": "Thumb / lateral forearm"},
    {"level": "C7", "area": "Middle finger"},
    {"level": "C8", "area": "Little finger / medial forearm"},
    {"level": "T1", "area": "Medial upper arm"},
    {"level": "T4", "area": "Nipple line"},
    {"level": "T10", "area": "Umbilicus"},
    {"level": "L1", "area": "Proximal 1/3 of thigh / inguinal region"},
    {"level": "L2", "area": "Middle 1/3 of anterior thigh"},
    {"level": "L3", "area": "Distal 1/3 of thigh / above the knee"},
    {"level": "L4", "area": "Medial lower leg / medial malleolus"},
    {"level": "L5", "area": "Dorsum of foot / great toe"},
    {"level": "S1", "area": "Lateral foot / small toe"},
]


# ---------------------------------------------------------------------------
# Myotomes (nerve root → muscle action)
# ---------------------------------------------------------------------------

MYOTOMES: list[dict] = [
    {"roots": "C5, C6", "action": "Shoulder abduction", "muscle": "Deltoid"},
    {"roots": "C5, C6", "action": "Elbow flexion", "muscle": "Biceps brachii"},
    {"roots": "C6, C7, C8", "action": "Wrist extension", "muscle": "Radial wrist extensors"},
    {"roots": "C6, C7, C8", "action": "Elbow extension", "muscle": "Triceps brachii"},
    {"roots": "C7, C8", "action": "Digit extension", "muscle": "Finger extensors (radial nerve)"},
    {"roots": "C8, T1", "action": "Digit abduction", "muscle": "Interossei (ulnar nerve)"},
    {"roots": "C8, T1", "action": "Thumb abduction", "muscle": "Abductor pollicis brevis (median nerve)"},
    {"roots": "L1, L2", "action": "Hip flexion", "muscle": "Iliopsoas"},
    {"roots": "L3, L4", "action": "Knee extension", "muscle": "Quadriceps"},
    {"roots": "L4", "action": "Ankle dorsiflexion", "muscle": "Tibialis anterior"},
    {"roots": "L5", "action": "Great toe extension", "muscle": "Extensor hallucis longus"},
    {"roots": "S1", "action": "Ankle plantarflexion", "muscle": "Gastrocnemius / soleus"},
    {"roots": "S1", "action": "Hip extension", "muscle": "Gluteus maximus"},
]


# ---------------------------------------------------------------------------
# Deep tendon reflexes
# ---------------------------------------------------------------------------

DTRS: list[dict] = [
    {"name": "Biceps reflex", "roots": "C5, C6"},
    {"name": "Brachioradialis reflex", "roots": "C5, C6"},
    {"name": "Triceps reflex", "roots": "C6, C7"},
    {"name": "Patellar (knee) reflex", "roots": "L2, L3, L4"},
    {"name": "Achilles (ankle) reflex", "roots": "S1"},
]


# ---------------------------------------------------------------------------
# Special tests (MSK — LE / UE / Spine)
# ---------------------------------------------------------------------------

SPECIAL_TESTS: list[dict] = [
    # Lower extremity — knee
    {
        "name": "Lachman test",
        "exam": "lower-extremity-msk",
        "joint": "Knee",
        "assesses": "ACL tear / laxity",
        "technique": "With knee flexed ~30°, stabilize the femur and pull the tibia anteriorly",
    },
    {
        "name": "Anterior drawer test",
        "exam": "lower-extremity-msk",
        "joint": "Knee",
        "assesses": "ACL tear / laxity",
        "technique": "With knee flexed 90° and foot stabilized, pull the tibia anteriorly",
    },
    {
        "name": "Posterior drawer test",
        "exam": "lower-extremity-msk",
        "joint": "Knee",
        "assesses": "PCL tear / laxity",
        "technique": "With knee flexed 90° and foot stabilized, push the tibia posteriorly",
    },
    {
        "name": "McMurray test",
        "exam": "lower-extremity-msk",
        "joint": "Knee",
        "assesses": "Meniscal tear",
        "technique": "Flex the knee, externally or internally rotate the tibia, then extend",
    },
    {
        "name": "Valgus stress test",
        "exam": "lower-extremity-msk",
        "joint": "Knee",
        "assesses": "MCL (medial collateral ligament) injury",
        "technique": "Apply valgus force to the knee at 0° and 30° of flexion",
    },
    {
        "name": "Varus stress test",
        "exam": "lower-extremity-msk",
        "joint": "Knee",
        "assesses": "LCL (lateral collateral ligament) injury",
        "technique": "Apply varus force to the knee at 0° and 30° of flexion",
    },
    {
        "name": "Bulge sign",
        "exam": "lower-extremity-msk",
        "joint": "Knee",
        "assesses": "Minor knee effusion",
        "technique": "Milk fluid medially then tap the lateral knee; watch for a bulge medially",
    },
    {
        "name": "Ballottement test",
        "exam": "lower-extremity-msk",
        "joint": "Knee",
        "assesses": "Major knee effusion",
        "technique": "Press the patella downward against the femur; a 'tap' indicates effusion",
    },
    {
        "name": "Thompson test",
        "exam": "lower-extremity-msk",
        "joint": "Ankle",
        "assesses": "Achilles tendon rupture",
        "technique": "With patient prone, squeeze the calf and watch for absent plantarflexion",
    },
    # Lower extremity — hip
    {
        "name": "FABER test",
        "exam": "lower-extremity-msk",
        "joint": "Hip",
        "assesses": "SI joint / hip pathology (groin strain)",
        "technique": "Flex, Abduct, and Externally Rotate the hip ('figure-4')",
    },
    {
        "name": "Trendelenburg test",
        "exam": "lower-extremity-msk",
        "joint": "Hip",
        "assesses": "Gluteus medius weakness",
        "technique": "Ask patient to stand on one leg; contralateral pelvis drop is positive",
    },
    # Upper extremity — shoulder
    {
        "name": "Empty can test",
        "exam": "upper-extremity-msk",
        "joint": "Shoulder",
        "assesses": "Supraspinatus tendon / tear",
        "technique": "Arms to 90°, internally rotated with thumbs down; resist downward pressure",
    },
    {
        "name": "Infraspinatus test",
        "exam": "upper-extremity-msk",
        "joint": "Shoulder",
        "assesses": "Infraspinatus tendon / tear",
        "technique": "Elbow at side, flexed 90°; patient externally rotates against resistance",
    },
    {
        "name": "Subscapularis test (lift-off)",
        "exam": "upper-extremity-msk",
        "joint": "Shoulder",
        "assesses": "Subscapularis tendon / tear",
        "technique": "Hand on lower back; patient lifts hand away from back against resistance",
    },
    {
        "name": "Crossed body adduction test",
        "exam": "upper-extremity-msk",
        "joint": "Shoulder",
        "assesses": "Acromioclavicular joint pathology",
        "technique": "Adduct the patient's arm across the chest",
    },
    # Upper extremity — wrist / hand
    {
        "name": "Phalen test",
        "exam": "upper-extremity-msk",
        "joint": "Wrist",
        "assesses": "Carpal tunnel syndrome",
        "technique": "Hold wrists fully flexed with dorsal surfaces pressed together for 1 minute",
    },
    {
        "name": "Tinel sign",
        "exam": "upper-extremity-msk",
        "joint": "Wrist",
        "assesses": "Carpal tunnel syndrome (median nerve)",
        "technique": "Tap over the volar carpal tunnel; tingling in median distribution is positive",
    },
    {
        "name": "Finkelstein test",
        "exam": "upper-extremity-msk",
        "joint": "Wrist",
        "assesses": "De Quervain tenosynovitis",
        "technique": "Patient clenches thumb inside fist; ulnarly deviate the wrist",
    },
    # Spine
    {
        "name": "Straight-leg raise",
        "exam": "spine-msk",
        "joint": "Lumbar spine",
        "assesses": "Sciatica / lumbar radiculopathy",
        "technique": "Patient supine, raise leg with knee extended; radicular pain is positive",
    },
]


# ---------------------------------------------------------------------------
# High-value per-exam facts — short, answerable, memorizable.
# Each fact yields one multiple-choice question. The distractors are all
# plausible wrong answers drawn from the same clinical domain.
# ---------------------------------------------------------------------------

KEY_FACTS: list[dict] = [
    # Breast & Axilla
    {
        "exam": "breast-axilla",
        "question": "In the Breast & Axilla exam, which lymph node group is palpated first as part of the central exam?",
        "answer": "Central axillary nodes",
        "distractors": [
            "Supraclavicular nodes",
            "Inguinal nodes",
            "Posterior cervical nodes",
        ],
    },
    {
        "exam": "breast-axilla",
        "question": "If the central axillary nodes feel large, hard, or tender, which other node groups should be palpated?",
        "answer": "Pectoral, lateral, suprascapular, and infra/supraclavicular nodes",
        "distractors": [
            "Only the contralateral axillary nodes",
            "Only the supraclavicular nodes",
            "The inguinal nodes",
        ],
    },
    {
        "exam": "breast-axilla",
        "question": "Which patient position during breast inspection is best for revealing skin dimpling or retraction?",
        "answer": "Hands pressed on hips with shoulders rolled forward",
        "distractors": [
            "Supine with arms at the side",
            "Prone with arms overhead",
            "Left lateral decubitus",
        ],
    },
    {
        "exam": "breast-axilla",
        "question": "Which technique is used to palpate the breast tissue bilaterally in the supine position?",
        "answer": "Chest wall sweep followed by bimanual digital palpation",
        "distractors": [
            "Single-finger tapping around the areola",
            "Percussion of the breast tissue",
            "Transillumination of the breast",
        ],
    },
    {
        "exam": "breast-axilla",
        "question": "Which of the following is NOT part of the standard inspection of the breast?",
        "answer": "Assess jugular venous pressure",
        "distractors": [
            "Compare size and symmetry",
            "Look for retractions or dimpling",
            "Inspect nipples for inversion",
        ],
    },

    # Female GU
    {
        "exam": "female-gu",
        "question": "In what position is the patient placed for the Female Genitourinary exam?",
        "answer": "Lithotomy position",
        "distractors": [
            "Left lateral decubitus",
            "Prone",
            "Standing",
        ],
    },
    {
        "exam": "female-gu",
        "question": "Before inserting the speculum, in which orientation is it initially held relative to the vaginal opening?",
        "answer": "Vertically (widest aspect vertical), with downward pressure against the perineum",
        "distractors": [
            "Horizontally, with upward pressure against the pubis",
            "Obliquely at 45°, pointing to the patient's left",
            "Vertically, with upward pressure against the clitoris",
        ],
    },
    {
        "exam": "female-gu",
        "question": "If a labial mass is seen on inspection, which gland is palpated?",
        "answer": "Bartholin gland",
        "distractors": [
            "Skene gland only",
            "Parotid gland",
            "Submandibular gland",
        ],
    },
    {
        "exam": "female-gu",
        "question": "During the Female GU exam, who must be present to satisfy chaperone requirements?",
        "answer": "A nurse or other HCP chaperone",
        "distractors": [
            "Only the patient's partner",
            "Another patient's family member",
            "No one — consent alone is sufficient",
        ],
    },
    {
        "exam": "female-gu",
        "question": "Which maneuver is used to assess for urinary incontinence and vaginal prolapse?",
        "answer": "Ask the patient to bear down",
        "distractors": [
            "Ask the patient to cough while seated",
            "Apply Credé pressure to the bladder",
            "Perform the straight-leg raise",
        ],
    },

    # Male GU
    {
        "exam": "male-gu",
        "question": "What is the preferred patient position for the Male GU exam?",
        "answer": "Standing (preferred), or lying supine with proper draping",
        "distractors": [
            "Lithotomy position",
            "Prone with legs abducted",
            "Left lateral decubitus",
        ],
    },
    {
        "exam": "male-gu",
        "question": "During inspection, what must be done with the foreskin of an uncircumcised patient?",
        "answer": "Retract it (or ask the patient to retract) and then replace it after the exam",
        "distractors": [
            "Leave it in place throughout the exam",
            "Apply lubricant and pin it back",
            "Cut and remove any adhesions",
        ],
    },
    {
        "exam": "male-gu",
        "question": "Which technique is used to distinguish a hydrocele from a solid scrotal mass?",
        "answer": "Transillumination of the scrotum",
        "distractors": [
            "Auscultation of the scrotum",
            "Percussion of the inguinal canal",
            "Palpation of the prostate",
        ],
    },
    {
        "exam": "male-gu",
        "question": "Which structure is palpated by inserting a finger into the scrotum and inviting the patient to cough?",
        "answer": "Inguinal canal (to feel for a hernia)",
        "distractors": [
            "Vas deferens for tenderness",
            "Testicular appendage",
            "Bulbocavernosus muscle",
        ],
    },

    # Lower Extremity MSK
    {
        "exam": "lower-extremity-msk",
        "question": "The anterior hip is palpated at which landmarks?",
        "answer": "Iliac crest, iliac tubercle, anterior-superior iliac spine, and pubic tubercle",
        "distractors": [
            "Greater trochanter, ischial tuberosity, and sacrum only",
            "Patella, tibial tuberosity, and fibular head",
            "Medial malleolus, calcaneus, and navicular",
        ],
    },
    {
        "exam": "lower-extremity-msk",
        "question": "Which special test screens for gluteus medius weakness?",
        "answer": "Trendelenburg test",
        "distractors": [
            "Lachman test",
            "McMurray test",
            "Thompson test",
        ],
    },
    {
        "exam": "lower-extremity-msk",
        "question": "Which maneuver is the 'figure-4' test used to evaluate hip or SI joint pathology?",
        "answer": "FABER (Flexion, Abduction, External Rotation)",
        "distractors": [
            "FADIR (Flexion, Adduction, Internal Rotation)",
            "Ober test",
            "Thomas test",
        ],
    },
    {
        "exam": "lower-extremity-msk",
        "question": "How is leg length measured?",
        "answer": "From the anterior superior iliac spine to the medial malleolus (crossing knee medially), bilaterally",
        "distractors": [
            "From the umbilicus to the great toe, unilaterally",
            "From the greater trochanter to the lateral malleolus, bilaterally",
            "From the pubic symphysis to the medial malleolus, bilaterally",
        ],
    },

    # Upper Extremity MSK
    {
        "exam": "upper-extremity-msk",
        "question": "The SITS muscles of the rotator cuff are:",
        "answer": "Supraspinatus, Infraspinatus, Teres minor, Subscapularis",
        "distractors": [
            "Supraspinatus, Infraspinatus, Teres major, Subscapularis",
            "Subclavius, Infraspinatus, Teres minor, Serratus",
            "Supraspinatus, Infraspinatus, Trapezius, Subscapularis",
        ],
    },
    {
        "exam": "upper-extremity-msk",
        "question": "Which landmarks are palpated on the elbow?",
        "answer": "Olecranon process, radial head, biceps brachii tendon, medial and lateral epicondyles",
        "distractors": [
            "Coracoid process, acromion, humeral head",
            "Scaphoid, lunate, capitate",
            "Clavicle, sternum, first rib",
        ],
    },
    {
        "exam": "upper-extremity-msk",
        "question": "Which special test is used to isolate the supraspinatus?",
        "answer": "Empty can test",
        "distractors": [
            "Finkelstein test",
            "Phalen test",
            "Hawkins impingement test",
        ],
    },

    # Spine
    {
        "exam": "spine-msk",
        "question": "Which special test screens for sciatica / lumbar radiculopathy?",
        "answer": "Straight-leg raise",
        "distractors": [
            "Spurling test",
            "Adson test",
            "Phalen test",
        ],
    },
    {
        "exam": "spine-msk",
        "question": "How should a patient stand for scoliosis screening?",
        "answer": "Knees straight, flexing forward at the waist while the examiner views from behind",
        "distractors": [
            "Arms overhead with the trunk extended",
            "Squatting with arms crossed",
            "Standing on one leg",
        ],
    },
    {
        "exam": "spine-msk",
        "question": "Which three regions of the spine are routinely inspected and palpated?",
        "answer": "Cervical, thoracic, and lumbar",
        "distractors": [
            "Cervical, sacral, and coccygeal",
            "Thoracic, lumbar, and sacral only",
            "Cervical and lumbar only",
        ],
    },

    # Neurologic
    {
        "exam": "neurologic",
        "question": "Which tuning fork frequency is used to assess vibratory sensation?",
        "answer": "128 Hz",
        "distractors": ["256 Hz", "512 Hz", "1024 Hz"],
    },
    {
        "exam": "neurologic",
        "question": "Where is vibratory sensation first tested on the foot?",
        "answer": "At the 1st MTP joint",
        "distractors": [
            "At the medial malleolus",
            "At the tip of the great toe",
            "At the heel",
        ],
    },
    {
        "exam": "neurologic",
        "question": "Pronator drift is elicited with the patient's eyes closed and arms held how?",
        "answer": "Arms held in front at 90° with palms up",
        "distractors": [
            "Arms crossed over the chest",
            "Arms held at the sides with fists clenched",
            "Arms fully abducted to 180° overhead",
        ],
    },
    {
        "exam": "neurologic",
        "question": "Stereognosis is tested by:",
        "answer": "Placing a familiar object in the patient's hand (eyes closed) and asking them to identify it",
        "distractors": [
            "Tracing a letter on the patient's palm (eyes closed)",
            "Touching both arms simultaneously",
            "Asking the patient to repeat a phrase",
        ],
    },
    {
        "exam": "neurologic",
        "question": "Graphesthesia is tested by:",
        "answer": "Tracing a number or letter on the patient's palm (eyes closed) and asking them to identify it",
        "distractors": [
            "Placing an object in the hand and asking them to identify it",
            "Touching both arms simultaneously",
            "Snapping fingers near each ear",
        ],
    },
    {
        "exam": "neurologic",
        "question": "Extinction is tested by:",
        "answer": "Touching both arms simultaneously and asking where the patient feels your touch",
        "distractors": [
            "Placing an object in the hand and asking them to identify it",
            "Tracing a letter on the palm",
            "Asking the patient to close their eyes and point to where they feel a pin",
        ],
    },
    {
        "exam": "neurologic",
        "question": "Intention tremor and past-pointing on finger-to-nose testing localize to:",
        "answer": "Ipsilateral cerebellar hemisphere",
        "distractors": [
            "Contralateral motor cortex",
            "Ipsilateral basal ganglia",
            "Contralateral thalamus",
        ],
    },
    {
        "exam": "neurologic",
        "question": "The MMSE is part of which portion of the neurologic exam?",
        "answer": "Mental status evaluation",
        "distractors": [
            "Cranial nerve exam",
            "Sensory exam",
            "Deep tendon reflex exam",
        ],
    },
    {
        "exam": "neurologic",
        "question": "Increased muscle tone on exam indicates:",
        "answer": "An upper motor neuron lesion",
        "distractors": [
            "A lower motor neuron lesion",
            "A peripheral nerve injury distal to the muscle",
            "Cerebellar dysfunction",
        ],
    },
]
