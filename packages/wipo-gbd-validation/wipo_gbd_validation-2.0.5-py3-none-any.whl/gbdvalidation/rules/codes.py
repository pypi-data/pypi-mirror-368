from gbdvalidation.rules import ErrorSeverity

ERROR_TYPE = {
    '1': {
        'severity': ErrorSeverity.CRITICAL,
        'type': 'Mandatory field missing'
    },
    '2': {
        'severity': ErrorSeverity.ERROR,
        'type': 'Conditional mandatory field missing'
    },
    '3': {
        'severity': ErrorSeverity.WARNING,
        'type': 'Invalid value'
    },
    '4': {
        'severity': ErrorSeverity.WARNING,
        'type': 'Undetected language'
    },
    '5': {
        'severity': ErrorSeverity.WARNING,
        'type': 'Wrong date'
    }
}

GROUP_TYPE = {
    '000': 'st13',
    '010': 'type',
    '020': 'kind',
    '030': 'markFeature',
    '040': 'registrationOfficeCode',
    '050': 'designatedCountries',
    '060': 'filingPlace',
    '070': 'reference.application|registration',
    '080': 'reference.office',
    '090': 'applicationNumber',
    '100': 'applicationDate',
    '110': 'registrationNumber',
    '120': 'registrationDate',
    '130': 'applicationLanguageCode',
    '140': 'secondLanguageCode',
    '150': 'expiryDate',
    '160': 'terminationDate',
    '170': 'officeStatus',
    '180': 'gbdStatus',
    '190': 'statusDate',
    '200': 'markDisclaimerDetails',
    '201': 'markDisclaimerDetails.text',
    '202': 'markDisclaimerDetails.languageCode',
    '211': 'wordMarkSpecification.markVerbalElement',
    '212': 'wordMarkSpecification.markSignificantVerbalElement',
    '213': 'wordMarkSpecification.markTranslation',
    '214': 'wordMarkSpecification.markTransliteration',
    '220': 'markImageDetails',
    '221': 'markImageDetails.name',
    '222': 'markImageDetails.colourIndicator',
    '223': 'markImageDetails.colourClaimed',
    '225': 'markImageDetails.classification.kind',
    '226': 'markImageDetails.classification.version',
    '227': 'markImageDetails.classification.code',
    '230': 'markSoundDetails',
    '231': 'markSoundDetails.filename',
    '232': 'markSoundDetails.fileformat',
    '243': 'goodsServicesClassification.class.code',
    '244': 'goodsServicesClassification.class.terms',
    '250': 'priorities',
    '251': 'priorities.countryCode',
    '252': 'priorities.number',
    '253': 'priorities.date',
    '254': 'priorities.comment',
    '260': 'publications',
    '261': 'publications.identifier',
    '262': 'publications.date',
    '263': 'publications.section',
    '270': 'applicants',
    '271': 'applicants.fullName',
    '272': 'applicants.fullAddress',
    '273': 'applicants.countryCode',
    '274': 'applicants.identifier',
    '275': 'applicants.kind',
    '280': 'representatives',
    '281': 'representatives.fullName',
    '282': 'representatives.fullAddress',
    '283': 'representatives.countryCode',
    '284': 'representatives.identifier',
    '285': 'representatives.kind',
    '290': 'correspondence',
    '291': 'correspondence.fullName',
    '292': 'correspondence.fullAddress',
    '293': 'correspondence.countryCode',
    '300': 'events',
    '301': 'events.officeKind',
    '302': 'events.gbdKind',
    '303': 'events.date',
    '310': 'markDescriptionDetails',
    '311': 'markDescriptionDetails.text',
    '312': 'markDescriptionDetails.languageCode',
}


