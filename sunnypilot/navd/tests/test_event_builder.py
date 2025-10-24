from cereal import custom

from openpilot.sunnypilot.navd.event_builder import build_navigation_events


class MockSM(dict):
  def __init__(self, nav_msg):
    super().__init__()
    self['navigationd'] = nav_msg


class TestEventBuilder:
  def test_build_navigation_events(self):
    # These direction messages were taken courtesy of the autonomy repo <3
    nav_msg = custom.Navigationd.new_message()
    nav_msg.valid = True
    nav_msg.bannerInstructions = 'Turn right onto West Esplanade Drive'
    nav_msg.upcomingTurn = 'none'
    nav_msg.allManeuvers = [
      custom.Navigationd.Maneuver.new_message(distance=192.848, type='depart', modifier='none', instruction='Depart'),
      custom.Navigationd.Maneuver.new_message(distance=192.64264487162754, type='turn', modifier='right', instruction='Turn right onto West Esplanade Drive')
    ]

    events = build_navigation_events(MockSM(nav_msg))
    expected = [{
      'name': custom.OnroadEventSP.EventName.navigationBanner,
      'type': 'warning',
      'message': 'Turn right onto West Esplanade Drive in 192m',
    }]
    assert events == expected

  def test_upcoming_turn_override(self):
    nav_msg = custom.Navigationd.new_message()
    nav_msg.valid = True
    nav_msg.bannerInstructions = 'Continue straight bro'
    nav_msg.upcomingTurn = 'left'
    nav_msg.allManeuvers = [
      custom.Navigationd.Maneuver.new_message(distance=50.0, type='turn', modifier='left', instruction='Turn left')
    ]

    events = build_navigation_events(MockSM(nav_msg))
    expected = [{
      'name': custom.OnroadEventSP.EventName.navigationBanner,
      'type': 'warning',
      'message': 'Turning Left',
    }]
    assert events == expected

  def test_sharp_turn_enhancement(self):
    nav_msg = custom.Navigationd.new_message()
    nav_msg.valid = True
    nav_msg.bannerInstructions = 'Turn right onto Main St'
    nav_msg.upcomingTurn = 'none'
    nav_msg.allManeuvers = [
      custom.Navigationd.Maneuver.new_message(distance=300.0, type='turn', modifier='none', instruction='Turn right onto Main St'),
      custom.Navigationd.Maneuver.new_message(distance=300.0, type='turn', modifier='sharp right', instruction='Take a sharp right onto Main St')
    ]

    events = build_navigation_events(MockSM(nav_msg))
    expected = [{
      'name': custom.OnroadEventSP.EventName.navigationBanner,
      'type': 'warning',
      'message': 'Take a sharp right onto Main St in 300m',
    }]
    assert events == expected
