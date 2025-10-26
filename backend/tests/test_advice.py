import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.services import advice

def test_evaluate_maize_ok():
    level, details = advice.evaluate_reading('maize', 20, 60)
    assert level == 'ok', f'Expected ok, got {level}'
    print('✅ test_evaluate_maize_ok passed')

def test_evaluate_maize_too_hot():
    level, details = advice.evaluate_reading('maize', 30, 60)
    assert level == 'too_hot', f'Expected too_hot, got {level}'
    assert details['temp'] == 30
    print('✅ test_evaluate_maize_too_hot passed')

def test_evaluate_maize_too_humid():
    level, details = advice.evaluate_reading('maize', 20, 80)
    assert level == 'too_humid', f'Expected too_humid, got {level}'
    assert details['hum'] == 80
    print('✅ test_evaluate_maize_too_humid passed')

def test_evaluate_potatoes_ok():
    level, details = advice.evaluate_reading('potatoes', 8, 90)
    assert level == 'ok', f'Expected ok, got {level}'
    print('✅ test_evaluate_potatoes_ok passed')

def test_evaluate_potatoes_too_cold():
    level, details = advice.evaluate_reading('potatoes', 2, 90)
    assert level == 'too_cold', f'Expected too_cold, got {level}'
    print('✅ test_evaluate_potatoes_too_cold passed')

def test_format_message_en():
    msg = advice.format_message('too_hot', 'maize', 'en', temp=30)
    assert 'DANGER' in msg
    assert '30' in msg
    print('✅ test_format_message_en passed:', msg)

def test_format_message_sw():
    msg = advice.format_message('too_humid', 'maize', 'sw', hum=80)
    assert 'HATARI' in msg
    assert '80' in msg
    print('✅ test_format_message_sw passed:', msg)

if __name__ == '__main__':
    test_evaluate_maize_ok()
    test_evaluate_maize_too_hot()
    test_evaluate_maize_too_humid()
    test_evaluate_potatoes_ok()
    test_evaluate_potatoes_too_cold()
    test_format_message_en()
    test_format_message_sw()
    print('\n✅ All tests passed!')
