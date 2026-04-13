"""Hand-curated knowledge base for the med-study PE exams.

PDF-faithful — every fact in this file is directly traceable to the PDFs in
the `exams/` directory. If a fact isn't literally in the source PDF, it
doesn't go here. No inferred techniques, no textbook findings, no non-PDF
distractors.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# Cranial nerves — taken from Neuro Checklist.pdf
#
# `label`  — how the PDF groups the nerve(s) (some are combined in the PDF)
# `tests`  — each bullet that appears under that CN label in the PDF
# ---------------------------------------------------------------------------

CRANIAL_NERVES: list[dict] = [
    {
        "label": "CN I — Olfactory",
        "tests": [
            "Ask patient to occlude one nostril and identify smell bilaterally",
        ],
    },
    {
        "label": "CN II — Optic",
        "tests": [
            "Assess visual acuity using Snellen pocket chart at 14 in",
            "Report findings for OU, OD, OS",
            "Visual fields by confrontation",
            "Perform a fundoscopic exam bilaterally (optic disc, vessels, retinal pallor, hemorrhages)",
        ],
    },
    {
        "label": "CN III, IV, VI — Oculomotor, Trochlear & Abducens",
        "tests": [
            "Inspect size and shape of pupils bilaterally for asymmetry and size",
            "Assess direct and consensual pupillary reaction bilaterally using a light source",
            "Assess extraocular movements bilaterally observing for nystagmus, smooth pursuit, and ptosis",
            "Assess pupillary convergence and lens accommodation bilaterally",
        ],
    },
    {
        "label": "CN V — Trigeminal (Sensory & Motor)",
        "tests": [
            "Palpate temporal and masseter muscles as patient clenches teeth",
            "Assess sensation to light touch of the face in V1, V2, V3 distribution",
        ],
    },
    {
        "label": "CN VII — Facial",
        "tests": [
            "Observe face for asymmetry",
            "Ask patient to raise eyebrows, frown, close eyes while you try to open them, smile showing teeth, and puff out cheeks",
        ],
    },
    {
        "label": "CN VIII — Acoustic",
        "tests": [
            "Assess hearing by rubbing thumb and forefinger together 2 inches from each ear, or whisper test",
            "Verbalize Weber and Rinne tests if hearing loss is detected",
        ],
    },
    {
        "label": "CN IX & X — Glossopharyngeal & Vagus",
        "tests": [
            "Inspect symmetric rise of soft palate and that uvula is at midline when patient says 'ahh'",
            "Verbalize testing the gag reflex using a tongue blade",
        ],
    },
    {
        "label": "CN XI — Spinal Accessory",
        "tests": [
            "Assess sternocleidomastoid strength against resistance bilaterally (head/neck rotation)",
            "Assess strength of trapezii against resistance bilaterally (shoulder shrug)",
        ],
    },
    {
        "label": "CN XII — Hypoglossal",
        "tests": [
            "Inspect tongue for fasciculations or atrophy",
            "Assess that the tongue is at midline when the patient sticks out the tongue",
        ],
    },
]


# ---------------------------------------------------------------------------
# Dermatomes — taken verbatim from Neuro Checklist.pdf "Sensory" section
# ---------------------------------------------------------------------------

DERMATOMES: list[dict] = [
    {"level": "C5", "area": "Lateral upper arm"},
    {"level": "C6", "area": "Lateral forearm, index finger, and thumb"},
    {"level": "C7", "area": "Middle finger"},
    {"level": "C8", "area": "Medial forearm, ring, and little finger"},
    {"level": "T1", "area": "Medial upper arm"},
    {"level": "T10", "area": "Umbilical level"},
    {"level": "L1", "area": "Proximal 1/3 of thigh"},
    {"level": "L2", "area": "Middle 1/3 of thigh"},
    {"level": "L3", "area": "Distal 1/3 of thigh"},
    {"level": "L4", "area": "Medial lower leg, medial great toe"},
    {"level": "L5", "area": "Lateral lower leg, toes 2-4"},
    {"level": "S1", "area": "Lateral foot, lateral small toe"},
]


# ---------------------------------------------------------------------------
# Myotomes (nerve root → muscle action) — verbatim from Neuro "Muscle Strength"
# subsection of the PDF. The PDF lists multi-root groupings; each entry below
# is exactly one line from that section.
# ---------------------------------------------------------------------------

MYOTOMES: list[dict] = [
    {"action": "Shoulder abduction", "roots": "C5, C6"},
    {"action": "Elbow flexion", "roots": "C5, C6"},
    {"action": "Elbow extension", "roots": "C6, C7, C8"},
    {"action": "Wrist extension", "roots": "C6, C7, C8, Radial Nerve"},
    {"action": "Digit abduction", "roots": "C8, T1, Ulnar Nerve"},
    {"action": "Thumb abduction", "roots": "C8, T1, Median Nerve"},
    {"action": "Digit extension", "roots": "C7, C8, radial nerve"},
    {"action": "Hip flexion", "roots": "L2, L3, L4"},
    {"action": "Hip extension", "roots": "S1"},
    {"action": "Hip adduction", "roots": "L2, L3, L4"},
    {"action": "Hip abduction", "roots": "L4, L5, S1"},
    {"action": "Knee flexion", "roots": "L5, S1, S2"},
    {"action": "Knee extension", "roots": "L2, L3, L4"},
    {"action": "Ankle dorsiflexion", "roots": "L4, L5"},
    {"action": "Ankle plantar flexion", "roots": "S1"},
]


# ---------------------------------------------------------------------------
# Deep tendon reflexes — verbatim from Neuro "Deep Tendon Reflexes" subsection
# ---------------------------------------------------------------------------

DTRS: list[dict] = [
    {"name": "Biceps reflex", "roots": "C5, C6"},
    {"name": "Triceps reflex", "roots": "C6, C7"},
    {"name": "Brachioradialis reflex", "roots": "C5, C6"},
    {"name": "Patellar reflex", "roots": "L2, L3, L4"},
    {"name": "Ankle jerk (Achilles tendon)", "roots": "S1"},
]


# ---------------------------------------------------------------------------
# Special tests — taken verbatim from the LE, UE, Spine, and Neuro PDFs.
#
# `purpose`  — the parenthetical after the test name in the PDF (e.g.
#              "(meniscal tear)", "(ACL tear/laxity)")
# `exam`     — which exam the test lives in
# `section`  — the major section / joint where it appears in the PDF
# ---------------------------------------------------------------------------

SPECIAL_TESTS: list[dict] = [
    # Lower extremity
    {
        "name": "FABER test",
        "exam": "lower-extremity-msk",
        "section": "Hip",
        "purpose": "Groin strain",
    },
    {
        "name": "Trendelenburg test",
        "exam": "lower-extremity-msk",
        "section": "Hip",
        "purpose": "Gluteal weakness",
    },
    {
        "name": "McMurray test",
        "exam": "lower-extremity-msk",
        "section": "Knee",
        "purpose": "Meniscal tear",
    },
    {
        "name": "Lachman test",
        "exam": "lower-extremity-msk",
        "section": "Knee",
        "purpose": "ACL tear / laxity",
    },
    {
        "name": "Anterior drawer test",
        "exam": "lower-extremity-msk",
        "section": "Knee",
        "purpose": "ACL tear / laxity",
    },
    {
        "name": "Posterior drawer test",
        "exam": "lower-extremity-msk",
        "section": "Knee",
        "purpose": "PCL tear / laxity",
    },
    {
        "name": "Valgus stress test",
        "exam": "lower-extremity-msk",
        "section": "Knee",
        "purpose": "MCL",
    },
    {
        "name": "Varus stress test",
        "exam": "lower-extremity-msk",
        "section": "Knee",
        "purpose": "LCL",
    },
    {
        "name": "Bulge sign",
        "exam": "lower-extremity-msk",
        "section": "Knee",
        "purpose": "Assess knee for minor effusion",
    },
    {
        "name": "Ballottement test (Balloon sign)",
        "exam": "lower-extremity-msk",
        "section": "Knee",
        "purpose": "Assess knee for major effusion",
    },
    {
        "name": "Thompson test",
        "exam": "lower-extremity-msk",
        "section": "Ankle",
        "purpose": "Assess the integrity of the Achilles tendon",
    },
    # Upper extremity — shoulder
    {
        "name": "Empty can test",
        "exam": "upper-extremity-msk",
        "section": "Shoulder",
        "purpose": "Supraspinatus",
    },
    {
        "name": "Infraspinatus test",
        "exam": "upper-extremity-msk",
        "section": "Shoulder",
        "purpose": "Infraspinatus",
    },
    {
        "name": "Subscapularis test",
        "exam": "upper-extremity-msk",
        "section": "Shoulder",
        "purpose": "Subscapularis",
    },
    {
        "name": "Crossed body adduction test",
        "exam": "upper-extremity-msk",
        "section": "Shoulder",
        "purpose": "Acromioclavicular joint",
    },
    {
        "name": "Neer test",
        "exam": "upper-extremity-msk",
        "section": "Shoulder",
        "purpose": "Subacromial impingement",
    },
    {
        "name": "Hawkins test",
        "exam": "upper-extremity-msk",
        "section": "Shoulder",
        "purpose": "Subacromial impingement",
    },
    # Upper extremity — wrist / hand
    {
        "name": "Tinel sign",
        "exam": "upper-extremity-msk",
        "section": "Wrist",
        "purpose": "Carpal tunnel syndrome",
    },
    {
        "name": "Phalen test",
        "exam": "upper-extremity-msk",
        "section": "Wrist",
        "purpose": "Carpal tunnel syndrome",
    },
    {
        "name": "Thumb tenosynovitis (Finkelstein) test",
        "exam": "upper-extremity-msk",
        "section": "Wrist",
        "purpose": "Thumb tenosynovitis",
    },
    # Spine
    {
        "name": "Straight-leg raise",
        "exam": "spine-msk",
        "section": "Lumbar spine",
        "purpose": "Sciatica / lumbar radiculopathy",
    },
    {
        "name": "Spurling test",
        "exam": "spine-msk",
        "section": "Cervical spine",
        "purpose": "Cervical radiculopathy",
    },
    # Neuro — the Neuro PDF also lists special tests
    {
        "name": "Brudzinski sign",
        "exam": "neurologic",
        "section": "Special Tests",
        "purpose": "Meningitis",
    },
    {
        "name": "Kernig sign",
        "exam": "neurologic",
        "section": "Special Tests",
        "purpose": "Meningitis",
    },
    {
        "name": "Asterixis",
        "exam": "neurologic",
        "section": "Special Tests",
        "purpose": "Uremic encephalopathy",
    },
    {
        "name": "Plantar reflex (Babinski)",
        "exam": "neurologic",
        "section": "Special Tests",
        "purpose": "Upper motor neuron lesion",
    },
    {
        "name": "Romberg test",
        "exam": "neurologic",
        "section": "Special Tests",
        "purpose": "Proprioception / balance",
    },
    {
        "name": "Ankle clonus",
        "exam": "neurologic",
        "section": "Special Tests",
        "purpose": "Upper motor neuron lesion",
    },
]


# ---------------------------------------------------------------------------
# Key facts — each entry is a single, literal, unambiguous fact stated in the
# source PDFs. Distractors are drawn from the same clinical domain AND from
# other PDF content whenever possible. Anything not directly in a PDF is
# omitted.
# ---------------------------------------------------------------------------

KEY_FACTS: list[dict] = [
    # Breast & Axilla — quotes from the PDF
    {
        "exam": "breast-axilla",
        "question": "What is the initial patient position for the Breast & Axilla exam?",
        "answer": "Sitting on the exam table with arms at side, gown open to the front",
        "distractors": [
            "Supine with arms at sides, fully disrobed",
            "Standing upright with both arms overhead",
            "Left lateral decubitus with knees flexed",
        ],
    },
    {
        "exam": "breast-axilla",
        "question": "Per the PDF, which lymph nodes are the PRIMARY palpation target during the breast exam?",
        "answer": "Central axillary lymph nodes",
        "distractors": [
            "Pectoral lymph nodes",
            "Infraclavicular lymph nodes",
            "Supraclavicular lymph nodes",
        ],
    },
    {
        "exam": "breast-axilla",
        "question": "If the central axillary nodes feel large, hard, or tender, which additional nodes does the PDF instruct you to palpate?",
        "answer": "Pectoral, lateral, suprascapular, infra/supraclavicular",
        "distractors": [
            "Only the contralateral central axillary",
            "Submental and submandibular",
            "Inguinal and femoral",
        ],
    },
    {
        "exam": "breast-axilla",
        "question": "Which additional inspection positions does the PDF list for the breast exam?",
        "answer": "Arms extended overhead, hands pressed on hips with shoulders rolled forward, seated and leaning forward",
        "distractors": [
            "Supine with knees flexed, prone, and left lateral",
            "Trendelenburg, reverse Trendelenburg, sitting",
            "Squatting, kneeling, and standing on one leg",
        ],
    },

    # Female GU
    {
        "exam": "female-gu",
        "question": "In what position is the patient placed for the Female GU exam?",
        "answer": "Lithotomy position with genital region properly draped",
        "distractors": [
            "Left lateral decubitus with knees to chest",
            "Prone with legs abducted",
            "Standing with one foot on a stool",
        ],
    },
    {
        "exam": "female-gu",
        "question": "Per the PDF, how is the speculum initially inserted?",
        "answer": "Vertically (widest aspect vertical), applying downward pressure against the perineum, after separating the labia minora with the nondominant hand",
        "distractors": [
            "Horizontally, with upward pressure against the pubis",
            "Obliquely at 45°, pointing to the patient's left",
            "Vertically, with upward pressure against the clitoris",
        ],
    },
    {
        "exam": "female-gu",
        "question": "Once the speculum is inside the vagina, what does the PDF say to do next?",
        "answer": "Rotate the speculum so the widest aspect is horizontal, then advance with slight downward pressure",
        "distractors": [
            "Open the speculum immediately without rotating",
            "Withdraw 1 cm and re-insert",
            "Rotate so the widest aspect is at 45°",
        ],
    },
    {
        "exam": "female-gu",
        "question": "Which gland is palpated if a labial mass is seen on inspection?",
        "answer": "Bartholin glands",
        "distractors": [
            "Skene glands",
            "Parotid glands",
            "Cowper glands",
        ],
    },
    {
        "exam": "female-gu",
        "question": "Which maneuver does the PDF use to assess urinary incontinence and vaginal prolapse?",
        "answer": "Ask the patient to bear down",
        "distractors": [
            "Ask the patient to cough while seated",
            "Apply suprapubic pressure",
            "Perform the straight-leg raise",
        ],
    },
    {
        "exam": "female-gu",
        "question": "During the bimanual exam, how does the PDF say to palpate the ovaries/adnexa?",
        "answer": "Gently apply a downward sweeping pressure from the right lateral abdomen toward the vagina, then repeat on the left",
        "distractors": [
            "Press firmly on the suprapubic area while the patient valsalvas",
            "Palpate directly over the sacroiliac joints",
            "Use a single-finger internal exam only",
        ],
    },
    {
        "exam": "female-gu",
        "question": "Per the PDF, what device is used for PAP smear specimen collection?",
        "answer": "A PAP smear broom inserted into the cervical os and turned in a circle 3 times, then dropped into liquid cytology",
        "distractors": [
            "A sterile cotton swab rotated 360° at the cervical os",
            "A suction catheter inserted through the cervical os",
            "A cytology brush swept across the vaginal walls",
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
            "Left lateral decubitus with knees flexed",
        ],
    },
    {
        "exam": "male-gu",
        "question": "What does the PDF say to do with the foreskin of an uncircumcised patient?",
        "answer": "Retract it (or ask the patient to retract it), then replace it after the exam",
        "distractors": [
            "Leave it in place throughout the exam",
            "Apply lubricant and pin it back",
            "Remove any adhesions with a sterile cotton swab",
        ],
    },
    {
        "exam": "male-gu",
        "question": "How does the PDF say to elevate the scrotum for posterior inspection?",
        "answer": "Elevate the scrotum to visualize the posterior aspect (may ask the patient to lift it)",
        "distractors": [
            "Palpate the perineum instead",
            "Have the patient bend over the exam table",
            "Use a tongue depressor to retract the scrotum inferiorly",
        ],
    },
    {
        "exam": "male-gu",
        "question": "Where does the PDF locate the epididymis?",
        "answer": "On the superior posterior surface of the testes",
        "distractors": [
            "At the anterior-inferior pole of the testes",
            "Within the spermatic cord above the testes",
            "Along the medial surface of the testes",
        ],
    },
    {
        "exam": "male-gu",
        "question": "What is the position for the rectal portion of the male GU exam?",
        "answer": "Lateral decubitus with knees bent, or standing leaning forward over the exam table",
        "distractors": [
            "Supine with legs in stirrups",
            "Prone with hips flexed at 90°",
            "Seated upright on the exam table",
        ],
    },

    # Lower Extremity MSK
    {
        "exam": "lower-extremity-msk",
        "question": "Which landmarks does the PDF list for palpating the anterior hip?",
        "answer": "Iliac crest, iliac tubercle, anterior-superior iliac spine, and pubic tubercle",
        "distractors": [
            "Greater trochanter, ischial tuberosity, and sacrum",
            "Patella, tibial tuberosity, and fibular head",
            "Medial malleolus, calcaneus, and navicular",
        ],
    },
    {
        "exam": "lower-extremity-msk",
        "question": "Which landmarks does the PDF list for palpating the posterior hip?",
        "answer": "Posterior-superior iliac spine, ischial tuberosity, and sacroiliac joint",
        "distractors": [
            "Greater trochanter, coccyx, and sacroiliac joint",
            "Iliac crest, pubic symphysis, and coccyx",
            "Lumbar spinous processes and iliac tubercle",
        ],
    },
    {
        "exam": "lower-extremity-msk",
        "question": "How is leg length measured per the PDF?",
        "answer": "From the anterior iliac spine to the medial malleolus, crossing the knee on the medial side, bilaterally",
        "distractors": [
            "From the umbilicus to the great toe, unilaterally",
            "From the greater trochanter to the lateral malleolus, bilaterally",
            "From the pubic symphysis to the lateral malleolus, bilaterally",
        ],
    },
    {
        "exam": "lower-extremity-msk",
        "question": "Per the PDF, what is the normal base width of gait?",
        "answer": "2-4 inches from heel to heel",
        "distractors": [
            "1-2 inches from heel to heel",
            "4-6 inches from heel to heel",
            "6-8 inches from heel to heel",
        ],
    },

    # Upper Extremity MSK
    {
        "exam": "upper-extremity-msk",
        "question": "Which rotator-cuff muscles does the PDF list as the SITS muscles?",
        "answer": "Supraspinatus, infraspinatus, teres minor, subscapularis",
        "distractors": [
            "Supraspinatus, infraspinatus, teres major, subscapularis",
            "Subclavius, infraspinatus, teres minor, serratus anterior",
            "Supraspinatus, infraspinatus, trapezius, subscapularis",
        ],
    },
    {
        "exam": "upper-extremity-msk",
        "question": "Which landmarks does the PDF list for palpating the elbow?",
        "answer": "Olecranon process, radial head, biceps brachii tendon, medial epicondyle, lateral epicondyle",
        "distractors": [
            "Coracoid process, acromion, humeral head",
            "Scaphoid, lunate, capitate",
            "Clavicle, sternum, first rib",
        ],
    },
    {
        "exam": "upper-extremity-msk",
        "question": "Which landmarks does the PDF list for palpating the shoulder?",
        "answer": "Sternoclavicular joint, clavicle, acromioclavicular joint, coracoid process, greater tubercle, biceps tendon at bicipital groove",
        "distractors": [
            "Olecranon, radial head, medial/lateral epicondyles",
            "Anatomic snuffbox, carpals, metacarpals",
            "Iliac crest, pubic tubercle, anterior-superior iliac spine",
        ],
    },

    # Spine
    {
        "exam": "spine-msk",
        "question": "Which regions of the spine does the PDF inspect and palpate?",
        "answer": "Cervical, thoracic, and lumbar",
        "distractors": [
            "Cervical, sacral, and coccygeal",
            "Thoracic, lumbar, and sacral only",
            "Cervical and lumbar only",
        ],
    },
    {
        "exam": "spine-msk",
        "question": "Per the PDF, how is the scoliosis screen performed?",
        "answer": "Patient stands with knees straight and flexes forward at the waist; inspect for spine curvature and asymmetry",
        "distractors": [
            "Patient stands with arms overhead and trunk extended",
            "Patient squats with arms crossed",
            "Patient stands on one leg with eyes closed",
        ],
    },
    {
        "exam": "spine-msk",
        "question": "Per the PDF, what structures are palpated during the spine exam?",
        "answer": "Paraspinous muscle, spinous processes, facet joints, vertebrae, sacroiliac joint",
        "distractors": [
            "Iliopsoas, gluteus maximus, hamstrings",
            "Deltoid, trapezius, rhomboids",
            "Scapula, clavicle, sternum",
        ],
    },

    # Neurologic
    {
        "exam": "neurologic",
        "question": "Which tuning fork frequency does the PDF specify for vibratory sensation?",
        "answer": "128 Hz",
        "distractors": ["256 Hz", "512 Hz", "1024 Hz"],
    },
    {
        "exam": "neurologic",
        "question": "Where on the foot does the PDF first test vibratory sensation?",
        "answer": "At the 1st MTP joint",
        "distractors": [
            "At the medial malleolus",
            "At the tip of the great toe",
            "At the heel",
        ],
    },
    {
        "exam": "neurologic",
        "question": "Per the PDF, how are the arms held to elicit pronator drift?",
        "answer": "Patient closes eyes and holds both arms in front at a 90° angle",
        "distractors": [
            "Arms crossed over the chest",
            "Arms held at the sides with fists clenched",
            "Arms fully abducted overhead",
        ],
    },
    {
        "exam": "neurologic",
        "question": "Per the PDF, how is stereognosis tested?",
        "answer": "Have patient close eyes and identify two objects placed in their hand one at a time",
        "distractors": [
            "Trace a number or letter on the patient's palm",
            "Touch both arms simultaneously",
            "Ask the patient to identify a sound near each ear",
        ],
    },
    {
        "exam": "neurologic",
        "question": "Per the PDF, how is graphesthesia tested?",
        "answer": "Have patient close eyes; trace a number or letter on the patient's palm and ask them to identify it",
        "distractors": [
            "Place an object in the hand and ask them to identify it",
            "Touch both arms simultaneously",
            "Apply sharp and dull stimuli to the palm",
        ],
    },
    {
        "exam": "neurologic",
        "question": "Per the PDF, how is extinction tested?",
        "answer": "Have patient close eyes; touch each arm individually, then simultaneously touch corresponding areas on both arms and ask where they feel your touch",
        "distractors": [
            "Place an object in the hand and ask them to identify it",
            "Trace a letter on the palm",
            "Ask the patient to point to where they feel a pin",
        ],
    },
    {
        "exam": "neurologic",
        "question": "Per the PDF, what does increased muscle tone indicate?",
        "answer": "An upper motor neuron lesion",
        "distractors": [
            "A lower motor neuron lesion",
            "A peripheral nerve injury distal to the muscle",
            "Cerebellar dysfunction",
        ],
    },
    {
        "exam": "neurologic",
        "question": "Per the PDF, what does decreased muscle tone indicate?",
        "answer": "A lower motor neuron lesion",
        "distractors": [
            "An upper motor neuron lesion",
            "A cerebellar hemispheric lesion",
            "A basal ganglia lesion",
        ],
    },
    {
        "exam": "neurologic",
        "question": "Per the PDF, the MMSE is part of which section of the neurologic exam?",
        "answer": "Mental Status Evaluation",
        "distractors": [
            "Cranial nerve exam",
            "Sensory exam",
            "Deep tendon reflex exam",
        ],
    },
    {
        "exam": "neurologic",
        "question": "Per the PDF, how does the Romberg test begin?",
        "answer": "Patient stands with both feet together, arms at side, with eyes open; if stable, close eyes and stand for 20-30 sec",
        "distractors": [
            "Patient stands on one leg with eyes open for 30 sec",
            "Patient walks heel-to-toe along a straight line",
            "Patient stands with feet apart while the examiner pushes laterally",
        ],
    },
    {
        "exam": "neurologic",
        "question": "Per the PDF, how is the Brudzinski sign elicited?",
        "answer": "Patient supine; passively flex the chin toward the sternum and observe for flexion of hips and knees",
        "distractors": [
            "Patient supine; passively extend the knee with hip flexed 90°",
            "Patient seated; tap the knee with a reflex hammer",
            "Patient prone; squeeze the calf and watch for ankle plantarflexion",
        ],
    },
    {
        "exam": "neurologic",
        "question": "Per the PDF, how is the Kernig sign elicited?",
        "answer": "Patient supine with hip and knee flexed at 90°; passively extend the knee",
        "distractors": [
            "Passively flex the chin toward the sternum",
            "Tap the lateral sole from heel to ball of foot",
            "Dorsiflex the foot and observe for rhythmic oscillations",
        ],
    },
    {
        "exam": "neurologic",
        "question": "Per the PDF, how is the plantar reflex (Babinski) elicited?",
        "answer": "Stroke the lateral aspect of the sole from the heel to the ball of the foot, curving medially across the ball",
        "distractors": [
            "Tap the Achilles tendon with a reflex hammer",
            "Squeeze the calf with the patient prone",
            "Flex the chin toward the sternum",
        ],
    },
]
