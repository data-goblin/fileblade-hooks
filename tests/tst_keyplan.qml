import QtQuick
import QtTest
import "../blades/KeyPlan.js" as KeyPlan

TestCase {
  name: "HooksKeyPlanRegression"

  readonly property int ctrl: Qt.ControlModifier
  readonly property int shift: Qt.ShiftModifier
  readonly property int alt: Qt.AltModifier
  readonly property int meta: Qt.MetaModifier

  function act(key, modifiers) {
    return KeyPlan.moduleAction(key, modifiers === undefined ? Qt.NoModifier : modifiers, Qt)
  }

  function test_tab_cycle_chords_are_never_consumed() {
    var chords = [Qt.Key_Tab, Qt.Key_Backtab, Qt.Key_PageUp, Qt.Key_PageDown,
                  Qt.Key_BracketLeft, Qt.Key_BracketRight]
    var mods = [ctrl, ctrl | shift, ctrl | alt, ctrl | meta, ctrl | shift | alt | meta]
    for (var c = 0; c < chords.length; c++) {
      for (var m = 0; m < mods.length; m++) {
        compare(act(chords[c], mods[m]), "", "chord " + c + " mods " + m)
        verify(KeyPlan.isTabCycle(chords[c], mods[m], Qt))
      }
    }
  }

  function test_tree_owned_focus_keys_are_not_claimed() {
    compare(act(Qt.Key_Tab), "")
    compare(act(Qt.Key_Backtab), "")
    compare(act(Qt.Key_Backtab, shift), "")
    compare(act(Qt.Key_Escape), "")
    compare(act(Qt.Key_N), "name")
    compare(act(Qt.Key_N, shift), "")
    compare(act(Qt.Key_N, Qt.ControlModifier), "")
  }

  function test_tree_owned_paging_and_jumps_are_not_claimed() {
    compare(act(Qt.Key_PageDown), "")
    compare(act(Qt.Key_PageUp), "")
    compare(act(Qt.Key_Home), "")
    compare(act(Qt.Key_End), "")
    compare(act(Qt.Key_D, ctrl), "")
    compare(act(Qt.Key_U, ctrl), "")
    compare(act(Qt.Key_G), "")
    compare(act(Qt.Key_G, shift), "")
  }

  function test_tree_owned_motions_are_not_claimed() {
    var owned = [Qt.Key_J, Qt.Key_K, Qt.Key_H, Qt.Key_L, Qt.Key_Up, Qt.Key_Down,
                 Qt.Key_Left, Qt.Key_Right, Qt.Key_Return, Qt.Key_Enter,
                 Qt.Key_O, Qt.Key_R, Qt.Key_Slash, Qt.Key_Z]
    for (var i = 0; i < owned.length; i++)
      compare(act(owned[i]), "", "owned index " + i)
  }

  function test_host_owned_alt_z_collapse_is_not_claimed() {
    compare(act(Qt.Key_Z, alt), "")
    compare(act(Qt.Key_Z, alt | shift), "")
  }

  function test_rescan_is_exact_shift_r_only() {
    compare(act(Qt.Key_R, shift), "rescan")
    compare(act(Qt.Key_R), "")
    compare(act(Qt.Key_R, ctrl), "")
    compare(act(Qt.Key_R, alt), "")
    compare(act(Qt.Key_R, meta), "")
    compare(act(Qt.Key_R, ctrl | shift), "")
    compare(act(Qt.Key_R, alt | shift), "")
    compare(act(Qt.Key_R, meta | shift), "")
  }

  function test_rescan_and_name_are_the_module_actions() {
    var keys = [Qt.Key_A, Qt.Key_B, Qt.Key_C, Qt.Key_D, Qt.Key_E, Qt.Key_F, Qt.Key_G,
                Qt.Key_H, Qt.Key_I, Qt.Key_J, Qt.Key_K, Qt.Key_L, Qt.Key_M, Qt.Key_N,
                Qt.Key_O, Qt.Key_P, Qt.Key_Q, Qt.Key_R, Qt.Key_S, Qt.Key_T, Qt.Key_U,
                Qt.Key_V, Qt.Key_W, Qt.Key_X, Qt.Key_Y, Qt.Key_Z, Qt.Key_Home, Qt.Key_End,
                Qt.Key_PageUp, Qt.Key_PageDown, Qt.Key_Tab, Qt.Key_Backtab, Qt.Key_Escape,
                Qt.Key_Return, Qt.Key_Enter, Qt.Key_Slash, Qt.Key_Space]
    var mods = [Qt.NoModifier, shift, ctrl, alt, meta, ctrl | shift, alt | shift, meta | shift]
    for (var k = 0; k < keys.length; k++) {
      for (var m = 0; m < mods.length; m++) {
        var action = act(keys[k], mods[m])
        var expected = (keys[k] === Qt.Key_R && mods[m] === shift) ? "rescan" : ((keys[k] === Qt.Key_N && mods[m] === Qt.NoModifier) ? "name" : "")
        compare(action, expected, "key " + k + " mods " + m)
      }
    }
  }
}
