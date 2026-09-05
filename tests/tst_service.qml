import QtQuick
import QtTest
import ".." as Hooks

TestCase {
  name: "HooksProviderService"
  Item { id: files }
  Component { id: providerComponent; Hooks.Service { manifest: ({ id: "test.hooks", __sourceDir: "/plugins/hooks" }) } }

  function test_cold_load_and_shared_observers() {
    var provider = createTemporaryObject(providerComponent, this)
    var view = { service: function() { return files }, ui: { url: function(name) {
      compare(name, "ArtifactInventory")
      return Qt.resolvedUrl("InventoryProbe.qml")
    } } }
    compare(provider.inventory, null)
    provider.attach(view)
    verify(provider.inventory !== null)
    compare(provider.inventory.files, files)
    compare(provider.inventory.providerId, "test.hooks")
    compare(provider.inventory.providerRoot, "/plugins/hooks")
    compare(provider.inventory.maximumItems, 1000)
    compare(provider.inventory.scanArguments, ["--watch"])
    var inventory = provider.inventory
    provider.attach(view)
    compare(inventory.observers.length, 1)
    var second = { ui: view.ui, service: view.service }
    provider.attach(second)
    compare(inventory.observers.length, 2)
    provider.detach(view); provider.detach(second)
    compare(inventory.observers.length, 0)
    provider.attach(view)
    compare(provider.inventory, inventory)
    compare(inventory.observers.length, 1)
  }
}
